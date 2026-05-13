from textual.app import App, ComposeResult
from textual.widgets import Header, DataTable, Label
from textual.containers import Horizontal, Vertical
from textual import work
import os
import main
from devices import *
from textual.reactive import reactive
from datetime import datetime
import tinytuya
from is_device_reachable import is_device_reachable
from send_email import send_email

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

REFRESH_INTERVAL_TUI = 120       
REFRSH_INTERVAL_EMAIL = 3600
LOG_FILE = os.getenv("LOG_FILE")


class TuyaDashboard(App):
    CSS = CSS
    last_updated: reactive[str] = reactive("Never")
    scanning: reactive[bool] = reactive(False)

    def on_mount(self) -> None:
        self.set_interval(REFRESH_INTERVAL_TUI, self.refresh_devices)
        self.set_interval(REFRSH_INTERVAL_EMAIL, self._send_alert_async)
        self.refresh_devices()

    def watch_last_updated(self, value: str) -> None:
        if not self.scanning:
            self.sub_title = f"Last updated: {value}"

    def watch_scanning(self, value: bool) -> None:
        self.sub_title = "🔍 Scanning network..." if value else f"Last updated: {self.last_updated}"

    @work(thread=True)
    def refresh_devices(self) -> None:
        if os.path.exists(LOG_FILE):
            open(LOG_FILE, "w", encoding="utf-8").close()
        self.call_from_thread(setattr, self, "scanning", True)
        tinytuya.deviceScan()
        devices = main.load_devices()
        my_devices, my_outside_devices = main.organize_devices(devices)
        floor_data = my_devices.get("Floors", [])
        self.call_from_thread(self._update_tables, floor_data, my_outside_devices)

    def _update_tables(self, floor_data, my_outside_devices) -> None:
        table_iter = iter(self.query(DataTable))
        for floor in floor_data:
            for room in floor:
                for device_dict, device_obj in zip(room.get("Devices", []), room.get("Objects", [])):
                    try:
                        table = next(table_iter)
                        table.clear(columns=True)
                        self.build_table(table, device_obj, device_dict)
                    except StopIteration:
                        self.log.warning(
                            "More devices in live data than DataTables in layout — "
                            "layout and data are out of sync. Restart the app to rebuild."
                        )
                        return

        for device_dict, device_obj in zip(my_outside_devices.get("Devices", []),my_outside_devices.get("Objects", [])):
            try:
                table = next(table_iter)
                table.clear(columns=True)
                self.build_table(table, device_obj, device_dict)
            except StopIteration:
                self.log.warning(
                    "More outside devices in live data than DataTables in layout — "
                    "layout and data are out of sync. Restart the app to rebuild."
                )
                return

        self.scanning = False
        self.last_updated = datetime.now().strftime("%H:%M:%S")

    @work(thread=True)
    def _send_alert_async(self) -> None:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                body = f.read()
            send_email(subject="Alerts from casa ganso", body=body)

    @staticmethod
    def clean_name(device_dict):
        name_raw = device_dict['name']
        if "s Q" in name_raw:
            return name_raw[:name_raw.index("s Q")]
        elif " Q" in name_raw:
            return name_raw[:name_raw.index(" Q")]
        return name_raw

    def build_table(self, table, device_obj, device_dict):
        _name = self.clean_name(device_dict)
        if device_obj is None:
            table.add_columns("Device", "Status")
            table.add_row(_name,"[bold white]unreachable[/]")
            return
        device_obj.refresh()
        _device_alerts = device_obj.get_alerts()
        _full_name = device_dict['name']
        if _device_alerts:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                _device_name = _full_name      
                f.write(f"{_device_name}\n")
                for alert in _device_alerts:
                    f.write(f"->{alert}\n")
                f.write("\n")
        device_obj.get_tui_table(table, _name)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        devices = main.load_devices()
        my_devices, my_outside_devices = main.organize_devices(devices)
        floor_data = my_devices.get("Floors", [])

        with Horizontal():
            for floor_idx, floor in enumerate(floor_data):
                with Vertical(classes="floor-container"):
                    yield Label(f"[bold red]Andar:{floor_idx}[/]")
                    for room_idx, room in enumerate(floor):
                        with Vertical(classes="room-container"):
                            yield Label(f"[bold yellow]Quarto:{room_idx + 1}[/]")
                            for device_dict, device_obj in zip(room.get("Devices", []), room.get("Objects", [])):
                                yield DataTable()

            with Vertical(classes="floor-container"):
                yield Label("[bold purple]OUTSIDE[/]")
                for device_dict, device_obj in zip(my_outside_devices.get("Devices", []),my_outside_devices.get("Objects", [])):
                    yield DataTable()


if __name__ == "__main__":
    TuyaDashboard().run()