from textual.app import App,ComposeResult
from textual.widgets import Header,DataTable,Label
from textual.containers import Horizontal,Vertical
from textual import work
import main
from devices import *
from textual.reactive import reactive
from datetime import datetime
import tinytuya

CSS = '''
.floor-container {
    width: 5fr;
    border: solid $primary;
    margin: 0;
    height: 1fr;
    overflow-y: scroll;
}
.room-container {
    height: auto;
    background: $surface;
    margin: 0;
    padding: 0;
    border-left: solid $primary-darken-1;
}
DataTable {
    height: auto;
    max-height: 5;
    margin: 0 1;
    border: none;
}
DataTable > .datatable--header {
    background: $primary-darken-3;
    text-style: bold;
}'''

REFRESH_INTERVAL = 60


class TuyaDashboard(App):
    CSS = CSS
    last_updated: reactive[str] = reactive("Never")
    scanning: reactive[bool] = reactive(False)

    def on_mount(self) -> None:
        self.set_interval(REFRESH_INTERVAL, self.refresh_devices)
        self.refresh_devices()

    def watch_last_updated(self, value: str) -> None:
        if not self.scanning:
            self.sub_title = f"Last updated: {value}"

    def watch_scanning(self, value: bool) -> None:
        self.sub_title = "🔍 Scanning network..." if value else f"Last updated: {self.last_updated}"

    @work(thread=True)
    def refresh_devices(self) -> None:
        self.call_from_thread(setattr, self, "scanning", True)
        tinytuya.deviceScan(False, 10)
        devices = main.load_devices()
        my_devices, my_outside_devices = main.organize_devices(devices)
        floor_data = my_devices.get("Floors", [])
        self.call_from_thread(self._update_tables, floor_data, my_outside_devices)

    def _update_tables(self, floor_data, my_outside_devices) -> None:
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

        for device_dict, device_obj in zip(
            my_outside_devices.get("Devices", []),
            my_outside_devices.get("Objects", [])):
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
        if "s Q" in name_raw:
            return name_raw[:name_raw.index("s Q")]
        elif " Q" in name_raw:
            return name_raw[:name_raw.index(" Q")]
        return name_raw

    def build_table(self, table, device_obj, device_dict):
        name = self.clean_name(device_dict)
        if device_obj is not None:
            device_obj.get_tui_table(table, name)
        else:
            table.add_columns("Device", "Status")
            table.add_row(name, "[bold white]Unreachable[/]")

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
                            for device_dict, device_obj in zip(
                                room.get("Devices", []), room.get("Objects", [])):
                                yield DataTable()

            with Vertical(classes="floor-container"):
                yield Label("[bold purple]OUTSIDE[/]")
                for device_dict, device_obj in zip(
                    my_outside_devices.get("Devices", []),
                    my_outside_devices.get("Objects", [])):
                    yield DataTable()



if __name__ == "__main__":
    TuyaDashboard().run()