from textual.app import App, ComposeResult
from textual.widgets import Header, DataTable, Label
from textual.containers import Horizontal, Vertical
from textual import work
import os
import time
import threading
import main
from devices import *
from send_email import send_email
from udp_listener import UDPListener
from energy_graph import GraphScreen
import tinytuya

DEVICES = main.load_devices()
MY_DEVICES, OUTSIDE_DEVICES = main.organize_devices(DEVICES)

MAX_CONCURRENT_POLLS  = 8
REFRESH_INTERVAL      = 2      ##local devices: poll every 5s (UDP handles real-time)
REFRESH_INTERVAL_CLOUD = 300   ##cloud devices (locks): poll every 5 minutes
REFRESH_INTERVAL_EMAIL = 3600
LOG_FILE = os.getenv("LOG_FILE")


def _iter_all_devices():
    """Yield (idx, device_dict, device_obj) for every device in order."""
    idx = 0
    for floor in MY_DEVICES.get("Floors", []):
        for room in floor:
            for d, o in zip(room.get("Devices", []), room.get("Objects", [])):
                yield idx, d, o
                idx += 1
    for d, o in zip(OUTSIDE_DEVICES.get("Devices", []), OUTSIDE_DEVICES.get("Objects", [])):
        yield idx, d, o
        idx += 1


CSS = '''
/* ─── Fullscreen layout ──────────────────────────────────────────── */
Screen {
    overflow: hidden;
}

#main {
    width: 100%;
    height: 100%;
}

/* Each floor fills the full screen height */
.floor-container {
    width: 1fr;
    height: 100%;
    margin: 0;
    overflow-y: scroll;
    border-right: tall $primary-darken-3;
}

/* Room sections stacked within a floor */
.room-container {
    height: auto;
    margin: 0 0 1 0;
    padding: 0 1;
    background: $surface;
    border-bottom: dashed $primary-darken-2;
}

/* ─── Tables fill available space ─── */
DataTable {
    height: auto;
    max-height: 100%;
    margin: 0;
    width: 100%;
}

DataTable > .datatable--header {
    background: $primary-darken-3;
    text-style: bold;
}
'''


class TuyaDashboard(App):
    CSS = CSS
    BINDINGS = [("g", "show_graphs", "Energy Graphs")]

    def on_mount(self) -> None:
        if LOG_FILE and os.path.exists(LOG_FILE):
            open(LOG_FILE, "w", encoding="utf-8").close()
        self.set_interval(REFRESH_INTERVAL_EMAIL, self._send_alert_async)

    def on_ready(self) -> None:
        """All widgets are mounted — populate tables immediately then start polling."""
        # Build device index: device_id → (table_id, device_dict, device_obj)
        self._device_index: dict[str, tuple] = {}
        for idx, device_dict, device_obj in _iter_all_devices():
            if device_obj is not None:
                self._device_index[device_obj.id] = (
                    f"device-table-{idx}", device_dict, device_obj
                )

        # Per-device flag: True means a UI update is already queued, don't
        # queue another one until the current one is rendered.
        self._update_pending: dict[str, bool] = {
            dev_id: False for dev_id in self._device_index
        }
        self._pending_lock = threading.Lock()

        # Start UDP listener for real-time updates
        self._udp = UDPListener(
            device_registry={
                dev_id: info[2] for dev_id, info in self._device_index.items()
            },
            on_update=self._on_udp_update,
        )
        self._udp.start()

        # Initial display with startup data (no network call)
        for idx, device_dict, device_obj in _iter_all_devices():
            self._update_single_table(f"device-table-{idx}", device_dict, device_obj)

        # Poll loop as fallback for devices that don't broadcast
        self._poll_loop()

    def action_show_graphs(self) -> None:
        """Collect energy history from all breakers and open the graph screen."""
        breaker_data = [
            (device_dict["name"], device_obj.get_energy_history())
            for _, device_dict, device_obj in _iter_all_devices()
            if device_obj is not None and hasattr(device_obj, "get_energy_history")
        ]
        self.push_screen(GraphScreen(breaker_data))

    def _on_udp_update(self, device_id: str, device_obj) -> None:
        """Called from the UDP listener thread — queue a UI update if none pending."""
        info = self._device_index.get(device_id)
        if info is None:
            return
        table_id, device_dict, _ = info

        with self._pending_lock:
            if self._update_pending.get(device_id):
                return   # already queued, skip duplicate
            self._update_pending[device_id] = True

        self.call_from_thread(
            self._update_single_table, table_id, device_dict, device_obj
        )

    @work(thread=True)
    def _poll_loop(self) -> None:
        """Fallback poll: local devices every REFRESH_INTERVAL, cloud devices
        (locks) every REFRESH_INTERVAL_CLOUD to conserve API quota."""
        all_devices = list(_iter_all_devices())
        semaphore   = threading.BoundedSemaphore(MAX_CONCURRENT_POLLS)

        # Separate local (have IP) from cloud (no IP — locks use cloud API)
        local_devices = [
            (idx, d, o) for idx, d, o in all_devices
            if o is not None and getattr(o, "ip", None)
        ]
        cloud_devices = [
            (idx, d, o) for idx, d, o in all_devices
            if o is not None and not getattr(o, "ip", None)
        ]

        cloud_counter = 0  # counts local poll cycles since last cloud poll
        cloud_every   = max(1, REFRESH_INTERVAL_CLOUD // REFRESH_INTERVAL)

        def poll_one(idx, device_dict, device_obj):
            dev_lock = self._udp.get_lock(device_obj.id)
            with semaphore:
                with dev_lock:
                    device_obj.refresh()

        while True:
            time.sleep(REFRESH_INTERVAL)
            cloud_counter += 1

            # Always poll local devices
            devices_to_poll = list(local_devices)

            # Only poll cloud devices every cloud_every cycles
            if cloud_counter >= cloud_every:
                devices_to_poll += cloud_devices
                cloud_counter = 0

            threads = [
                threading.Thread(target=poll_one, args=(idx, d, o), daemon=True)
                for idx, d, o in devices_to_poll
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # Push UI updates
            for idx, device_dict, device_obj in devices_to_poll:
                dev_id   = device_obj.id
                table_id = f"device-table-{idx}"
                with self._pending_lock:
                    if self._update_pending.get(dev_id):
                        continue
                    self._update_pending[dev_id] = True
                self.call_from_thread(
                    self._update_single_table, table_id, device_dict, device_obj
                )

    def _update_single_table(self, table_id: str, device_dict: dict, device_obj) -> None:
        # Clear the pending flag so the next update can be queued
        if device_obj is not None:
            with self._pending_lock:
                self._update_pending[device_obj.id] = False
        try:
            table = self.query_one(f"#{table_id}", DataTable)
        except Exception:
            return
        table.clear(columns=True)
        self._build_table(table, device_obj, device_dict)

    @work(thread=True)
    def _send_alert_async(self) -> None:
        if not LOG_FILE:
            return
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            body = f.read()
        send_email(subject="Alerts from casa ganso", body=body)

    @staticmethod
    def _clean_name(device_dict: dict) -> str:
        name_raw = device_dict["name"]
        for marker in ("s Q", " Q"):
            if marker in name_raw:
                return name_raw[: name_raw.index(marker)]
        return name_raw

    def _build_table(self, table, device_obj, device_dict) -> None:
        name = self._clean_name(device_dict)
        if device_obj is None:
            table.add_columns("Device", "Status")
            table.add_row(name, "[bold white]unreachable[/]")
            return
        if LOG_FILE:
            alerts = device_obj.get_alerts()
            if alerts:
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"{device_dict['name']}\n")
                    for alert in alerts:
                        f.write(f"->{alert}\n")
                    f.write("\n")
        device_obj.get_tui_table(table, name)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        floor_data = MY_DEVICES.get("Floors", [])
        idx = 0

        with Horizontal(id="main"):
            # One .floor-container per floor — scrolls independently
            for floor_idx, floor in enumerate(floor_data):
                with Vertical(classes="floor-container"):
                    yield Label(f"[bold red]Andar:{floor_idx}[/]")
                    for room_idx, room in enumerate(floor):
                        with Vertical(classes="room-container"):
                            yield Label(f"[bold yellow]Quarto:{room_idx + 1}[/]")
                            for _ in room.get("Devices", []):
                                yield DataTable(id=f"device-table-{idx}")
                                idx += 1

            # Outside gets its own .floor-container column
            with Vertical(classes="floor-container"):
                yield Label("[bold purple]OUTSIDE[/]")
                for _ in OUTSIDE_DEVICES.get("Devices", []):
                    yield DataTable(id=f"device-table-{idx}")
                    idx += 1


if __name__ == "__main__":
    try:
        TuyaDashboard().run()
    except KeyboardInterrupt:
        pass
