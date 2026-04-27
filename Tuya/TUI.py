from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label, Static, Switch
from textual.containers import Horizontal, Vertical
from textual import on, work
import main
from devices import *

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


class TuyaDashboard(App):
    CSS = CSS

                
    @staticmethod
    def clean_name(device_dict):
        name_raw = device_dict['name']
        name = name_raw
        if "s Q" in name_raw:
            name = name_raw[:name_raw.index("s Q")] if "s Q" in name_raw else name_raw
        elif "Q" in name_raw:
            name = name_raw[:name_raw.index("Q")] if "Q" in name_raw else name_raw
    
        return name
    
        
    def build_table(self, table, device_obj, device_dict):
       # Store references for the click handler

        if isinstance(device_obj, (breaker, consumption_breaker)):
            table.add_columns("Device", "Status", "State", "Error")
            name = self.clean_name(device_dict)
            status, state, details = device_obj.get_tui_info()
            table.add_row(name, status, state, details)
        elif isinstance(device_obj, contact_sensor):
            table.add_columns("Device", "Status", "Door State", "Battery")
            name = self.clean_name(device_dict)
            status, door_state, battery = device_obj.get_tui_info()
            table.add_row(name, status, door_state, battery)
        elif isinstance(device_obj, esmax):
            table.add_columns("Device", "Status", "Lock State", "Battery")
            name = self.clean_name(device_dict)
            status, state_lock, battery = device_obj.get_tui_info()
            table.add_row(name, status, state_lock, battery)
        elif isinstance(device_obj, general_circuit_breaker):
            table.add_columns("Device", "Status", "State", "Error")
            name_raw = device_dict['name']
            name = name_raw[:name_raw.index("s Q")] if "s Q" in name_raw else name_raw
            status, state, error = device_obj.get_tui_info()
            table.add_row(name, status, state, error)
        elif isinstance(device_obj, heater):
            table.add_columns("Device", "Status", "Power")
            name = self.clean_name(device_dict)
            status, details = device_obj.get_tui_info()
            table.add_row(name, status, details)
        elif isinstance(device_obj, lock):
            table.add_columns("Device", "Status", "Door State", "Battery")
            name = self.clean_name(device_dict)
            status, door_state, battery = device_obj.get_tui_info()
            table.add_row(name, status, door_state, battery)
        elif isinstance(device_obj, presence_sensor):
            table.add_columns("Device", "Status", "Presence")
            name = self.clean_name(device_dict)
            status, presence = device_obj.get_tui_info()
            table.add_row(name, status, presence)
        elif isinstance(device_obj, smart_bulb):
            table.add_columns("Device", "Status", "LED")
            name = self.clean_name(device_dict)
            status, led = device_obj.get_tui_info()
            table.add_row(name, status, led)
        elif isinstance(device_obj, smart_ir):
            table.add_columns("Device", "Status")
            name = self.clean_name(device_dict)
            status = device_obj.get_tui_info()
            table.add_row(name, status)
        elif isinstance(device_obj, smart_lock):
            table.add_columns("Device", "Status", "Battery", "Lock")
            name = self.clean_name(device_dict)
            status, battery, state = device_obj.get_tui_info()
            table.add_row(name, status, battery, state)
        elif isinstance(device_obj, smart_plug):
            table.add_columns("Device", "Status", "State")
            name = self.clean_name(device_dict)
            status, state = device_obj.get_tui_info()
            table.add_row(name, status, state)
        elif isinstance(device_obj, smart_tv):
            table.add_columns("Device", "Status", "Power")
            name = self.clean_name(device_dict)
            status, power = device_obj.get_tui_info()
            table.add_row(name, status, power)
        else:
            table.add_columns("Device", "Status")
            name = self.clean_name(device_dict)
            status = "[bold white]Unreachable[/]"
            table.add_row(name, status)
            
            
        return table
            
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        devices = main.load_devices()
        my_devices, my_outside_devices = main.organize_devices(devices)
        floor_data = my_devices.get("Floors", [])

        with Horizontal():
            # Uma coluna por cada andar
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

            # Dispositivos "outside"
            with Vertical(classes="floor-container"):
                yield Label("[bold purple]OUTSIDE[/]")
                for device_dict, device_obj in zip(my_outside_devices.get("Devices", []), my_outside_devices.get("Objects", [])):
                    out_table = DataTable()
                    self.build_table(out_table, device_obj, device_dict)
                    yield out_table

        yield Footer()

if __name__ == "__main__":
    TuyaDashboard().run()
