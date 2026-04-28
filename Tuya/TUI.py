import subprocess
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label, Static, Switch
from textual.containers import Horizontal, Vertical
from textual import on, work
import main
from devices import *
from textual.reactive import reactive
from datetime import datetime
import tinytuya

CSS = '''
/* Each floor is a column */
.floor-container {
    width: 1fr;
    border: solid $primary;
    margin: 1;
    height: 100%;
    overflow-y: auto;
}

/* Group of tables for one room */
.room-container {
    height: auto;
    background: $surface;
    margin: 1;
    padding: 1;
    border-left: solid $primary-darken-1;
}

/* Make individual device tables compact */
DataTable {
    height: auto;
    max-height: 9;
    margin: 0 1;
    border: none;
}

DataTable > .datatable--header {
    background: $primary-darken-3;
    text-style: bold;
}'''


REFRESH_INTERVAL = 30  # seconds


class TuyaDashboard(App):
    CSS = CSS
    last_updated: reactive[str] = reactive("Never")
    scanning: reactive[bool] = reactive(False)

    def on_mount(self) -> None:
        self.set_interval(REFRESH_INTERVAL, self.refresh_devices)

    def watch_last_updated(self, value: str) -> None:
        if not self.scanning:
            self.sub_title = f"Last updated: {value}"

    def watch_scanning(self, value: bool) -> None:
        self.sub_title = "🔍 Scanning network..." if value else f"Last updated: {self.last_updated}"

    @work(thread=True)
    def refresh_devices(self) -> None:
        """Runs in background thread — scans network, then reloads devices."""
        # Show scanning indicator
        self.call_from_thread(setattr, self, "scanning", True)

        #Direct library call (Replaces subprocess)
        #This updates 'devices.json' in the local directory by default
        tinytuya.deviceScan(False,10)

        #Reload devices from the updated devices.json
        devices = main.load_devices()
        my_devices, my_outside_devices = main.organize_devices(devices)
        floor_data = my_devices.get("Floors", [])
        # Update UI
        self.call_from_thread(self._update_tables, floor_data, my_outside_devices)

    def _update_tables(self, floor_data, my_outside_devices) -> None:
        """Runs on UI thread — safely updates all DataTables."""
        table_iter = iter(self.query(DataTable))

        for floor in floor_data:
            for room in floor:
                for device_dict, device_obj in zip(
                    room.get("Devices", []), room.get("Objects", [])):
                    try:
                        table = next(table_iter)
                        table.clear(columns=True)
                        self.build_table(table, device_obj, device_dict)
                    except StopIteration:
                        return

        for device_dict, device_obj in zip(my_outside_devices.get("Devices", []), my_outside_devices.get("Objects", [])):
            try:
                table = next(table_iter)
                table.clear(columns=True)
                self.build_table(table, device_obj, device_dict)
            except StopIteration:
                return

        self.scanning = False
        self.last_updated = datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def clean_name(device_dict):
        name_raw = device_dict['name']
        name = name_raw
        if "s Q" in name_raw:
            name = name_raw[0:name_raw.index("s Q")]
        elif "Q" in name_raw:
            name = name_raw[0:name_raw.index("Q")]
        return name

    def build_table(self, table, device_obj, device_dict):
        if isinstance(device_obj, (breaker, consumption_breaker)):
            name = self.clean_name(device_dict)
            table = device_obj.get_tui_table(table,name)
        elif isinstance(device_obj, contact_sensor):
            name = self.clean_name(device_dict)
            table = device_obj.get_tui_table(table,name)
        elif isinstance(device_obj, esmax):
            name = self.clean_name(device_dict)
            table = device_obj.get_tui_table(table,name)
        elif isinstance(device_obj, general_circuit_breaker):
            name = self.clean_name(device_dict)
            table = device_obj.get_tui_tanle(table,name)
        elif isinstance(device_obj, heater):
            name = self.clean_name(device_dict)
            table = device_obj.get_tui_table(table,name)
        elif isinstance(device_obj, lock):
            name = self.clean_name(device_dict)
            table = device_obj.get_tui_info(table,name)
        elif isinstance(device_obj, presence_sensor):
            name = self.clean_name(device_dict)
            table= device_obj.get_tui_info(table,name)
        elif isinstance(device_obj, smart_bulb):
            name = self.clean_name(device_dict)
            table = device_obj.get_tui_table(table,name)
        elif isinstance(device_obj, smart_ir):
            name = self.clean_name(device_dict)
            status = device_obj.get_tui_table(table,name)
        elif isinstance(device_obj, smart_lock):
            name = self.clean_name(device_dict)
            status, battery, state = device_obj.get_tui_table(table,name)
        elif isinstance(device_obj, smart_plug):
            name = self.clean_name(device_dict)
            status, state = device_obj.get_tui_table(table,name)
        elif isinstance(device_obj, smart_tv):
            name = self.clean_name(device_dict)
            status, power = device_obj.get_tui_table(table,name)
        else:
            name = self.clean_name(device_dict)
            status = "[bold white]Unreachable[/]"
            table.add_columns("Device", "Status")
            table.add_row(name, status)

        return table

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
                                table = DataTable()
                                self.build_table(table, device_obj, device_dict)
                                yield table

            with Vertical(classes="floor-container"):
                yield Label("[bold purple]OUTSIDE[/]")
                for device_dict, device_obj in zip(my_outside_devices.get("Devices", []), my_outside_devices.get("Objects", [])):
                    out_table = DataTable()
                    self.build_table(out_table, device_obj, device_dict)
                    yield out_table

        yield Footer()


if __name__ == "__main__":
    TuyaDashboard().run()