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

DEVICES = main.load_devices()
MY_DEVICES, OUTSIDE_DEVICES = main.organize_devices(DEVICES)

MAX_CONCURRENT_POLLS = 8
REFRESH_INTERVAL = 5
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
.floor-container {
    width: 1fr;
    margin: 0;
    height: 1fr;
    overflow-y: scroll;
}
.room-container {
    height: auto;
    background: $surface;
    margin: 0;
    padding: 0;
}
DataTable {
    height: auto;
    max-height: 1fr;
    margin: 0 0;
}
DataTable > .datatable--header {
    background: $primary-darken-3;
}'''


class TuyaDashboard(App):
    CSS = CSS

    def on_mount(self) -> None:
        if LOG_FILE and os.path.exists(LOG_FILE):
            open(LOG_FILE, "w", encoding="utf-8").close()
        self.set_interval(REFRESH_INTERVAL_EMAIL, self._send_alert_async)

    def on_ready(self) -> None:
        """All widgets are mounted — populate tables immediately then start polling."""
        for idx, device_dict, device_obj in _iter_all_devices():
            self._update_single_table(f"device-table-{idx}", device_dict, device_obj)
        self._poll_loop()

    @work(thread=True)
    def _poll_loop(self) -> None:
        """Single background thread: polls all devices concurrently then updates UI."""
        all_devices = list(_iter_all_devices())
        semaphore = threading.BoundedSemaphore(MAX_CONCURRENT_POLLS)
        results: dict = {}
        lock = threading.Lock()

        def poll_one(idx, device_dict, device_obj):
            if device_obj is not None:
                with semaphore:
                    device_obj.refresh()
            with lock:
                results[idx] = (device_dict, device_obj)

        while True:
            time.sleep(REFRESH_INTERVAL)
            threads = [
                threading.Thread(target=poll_one, args=(idx, d, o), daemon=True)
                for idx, d, o in all_devices
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            with lock:
                snapshot = dict(results)
            for idx, (device_dict, device_obj) in snapshot.items():
                self.call_from_thread(
                    self._update_single_table,
                    f"device-table-{idx}",
                    device_dict,
                    device_obj,
                )

    def _update_single_table(self, table_id: str, device_dict: dict, device_obj) -> None:
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

        with Horizontal():
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
