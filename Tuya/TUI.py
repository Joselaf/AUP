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
}

/* Group of tables for one room */
.room-container {
    height: auto;
    background: $surface;
    margin: 1;
    padding: 1;
}

/* Container for Table + Switch alignment */
.device-wrapper {
    height: auto;
    /* FIX: Added 'left' to satisfy the 2-value requirement */
    align: left middle;
    margin-bottom: 1;
}

/* Make individual device tables compact */
DataTable {
    height: auto;
    max-height: 5;
    margin: 0 1; 
    border: none;
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
        table.device_instance = device_obj
        table.device_dict = device_dict
        table.cursor_type = "row"
        table.show_cursor = True
        table.styles.text_hover_style = "bold magenta"
        
        if len(table.columns) > 0:
            table.clear(columns=True) 

        if isinstance(device_obj, (breaker, consumption_breaker)):
            table.add_columns("Device", "Status","State","Error")
            name = self.clean_name(device_dict)
            status,state,details = device_obj.get_tui_info()
            table.add_row(name,status,state,details)
        elif isinstance(device_obj, contact_sensor):
            table.add_columns("Device", "Status","Door_state","Battery")
            name = self.clean_name(device_dict)
            status,door_state, battery = device_obj.get_tui_info()
            table.add_row(name, status, door_state, battery)
        elif isinstance(device_obj, esmax):
            table.add_columns("Device", "Status","State_Lock","Battery")
            name = self.clean_name(device_dict)
            status,state_lock,battery = device_obj.get_tui_info()
            table.add_row(name, status, state_lock, battery)
        elif isinstance(device_obj, general_circuit_breaker):
            table.add_columns("Device", "Status","State","Error")
            name_raw = device_dict['name']
            name = name_raw[:name_raw.index("s Q")] if "s Q" in name_raw else name_raw
            status, state,error = device_obj.get_tui_info()
            table.add_row(name,status,state,error)
        elif isinstance(device_obj, heater):
            table.add_columns("Device","Status","Power")
            name = self.clean_name(device_dict)
            status,details = device_obj.get_tui_info()
            table.add_row(name, status, details)
        elif isinstance(device_obj, lock):
            table.add_columns("Device", "Status","Door_state","Battery")
            name = self.clean_name(device_dict)
            status,door_state, battery = device_obj.get_tui_info()
            table.add_row(name, status, door_state, battery)
        elif isinstance(device_obj, presence_sensor):
            table.add_columns("Device","Status","Presence")
            name = self.clean_name(device_dict)
            status,presence = device_obj.get_tui_info()
            table.add_row(name,status,presence)
        elif isinstance(device_obj, smart_bulb):
            table.add_columns("Devices","Status","Led")
            name = self.clean_name(device_dict)
            status,led = device_obj.get_tui_info()
            table.add_row(name,status,led)
        elif isinstance(device_obj, smart_ir):
            table.add_columns("Device","Status")
            name = self.clean_name(device_dict)
            status = device_obj.get_tui_info()
            table.add_row(name,status)
        elif isinstance(device_obj, smart_lock):
            table.add_columns("Device","Status","Battery", "Lock")
            name = self.clean_name(device_dict)
            status,battery,state = device_obj.get_tui_info()
            table.add_row(name,status,battery,state)
        elif isinstance(device_obj, smart_plug):
            table.add_columns("Device","Status","State")
            name = self.clean_name(device_dict)
            status,state = device_obj.get_tui_info()
            table.add_row(name,status,state)
        elif isinstance(device_obj, smart_tv):
            table.add_columns("Device","Status","Power")
            name = self.clean_name(device_dict)
            status,power = device_obj.get_tui_info()
            table.add_row(name,status,power)
        else:
            table.add_columns("Device","Status")
            name = self.clean_name(device_dict)
            status = "[bold white]Unreacheble[/]"
            table.add_row(name,status)
            
            
        return table
            
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        devices = main.load_devices()
        my_devices, my_outside_devices = main.organize_devices(devices)
        floor_data = my_devices.get("Floors",[])
        with Horizontal():
            ##uma coluna por cada andar, e cada andar tem uma tabela com os dispositivos daquele andar
            for index, floor in enumerate(floor_data):
                with Vertical():
                    yield Label(f"[bold red]Andar:{index}[/]")
                    for index, room in enumerate(floor):
                                yield Label(f"[bold yellow]Quarto:{index+1}[/]")
                                for device_dict, device_obj in zip(room.get("Devices",[]), room.get("Objects",[])):
                                    table = DataTable() ## criamos a tabela por quarto
                                    table.device_instance = device_obj
                                    table.device_dict = device_dict 
                                    self.build_table(table,device_obj,device_dict)                                   
                                    yield table  

            ## 2. Criar uma tabela para os dispositivos "outside"
            with Vertical():
                yield Label("[bold purple]OUTSIDE[/]")
                for device_dict, device_obj in zip(my_outside_devices.get("Devices",[]),my_outside_devices.get("Objects",[])):
                    out_table = DataTable()
                    out_table.device_instance = device_obj  
                    out_table.device_dict = device_dict
                    self.build_table(out_table,device_obj, device_dict)
                    yield out_table
        
if __name__ == "__main__":
    TuyaDashboard().run()
