from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label, Static
from textual.containers import Horizontal, Vertical
import main
import time
from devices import *

CSS = '''/* Each floor is a column */
.floor-container {
    width: 1fr;
    border: tall $primary;
    margin: 1;
}

/* Group of tables for one room */
.room-container {
    height: auto;
    background: $surface;
    margin: 1;
    padding: 1;
}

/* Make individual device tables compact */
DataTable {
    height: auto;       /* Shrinks the table to only fit its rows */
    max-height: 5;      /* Prevents any one table from exploding in size */
    margin-bottom: 1;   /* Space between the tables */
    border: rounded $accent;
}
DataTable {
    /* This removes the extra empty lines and footers by shrinking 
       the widget to fit only the rows it actually has */
    height: auto;
    
    /* Removes the border that often contains the footer space */
    border: none;
    
    /* Optional: reduce the margin so tables sit close together */
    margin: 0 1; 
}

/* Specifically target the scrollbar if it still appears */
DataTable > .datatable--scrollbar {
    display: none;
}

'''

class TuyaDashboard(App): 
        
    def build_table(self, table, device_obj, device_dict):
        if isinstance(device_obj, (breaker, consumption_breaker)):
            table.add_columns("Device", "Status","State","Error")
            name = device_dict['name']
            status,state,details = device_obj.get_tui_info()
            table.add_row(name,status,state,details)
        elif isinstance(device_obj, contact_sensor):
            table.add_columns("Device", "Status","Door_state","Battery")
            name = device_dict['name']
            status,door_state, battery = device_obj.get_tui_info()
            table.add_row(name, status, door_state, battery)
        elif isinstance(device_obj, esmax):
            table.add_columns("Device", "Status","State_Lock","Battery")
            name = device_dict['name']
            status,state_lock,battery = device_obj.get_tui_info()
            table.add_row(name, status, state_lock, battery)
        elif isinstance(device_obj, general_circuit_breaker):
            table.add_columns("Device", "Status","State","Error")
            name = device_dict['name']
            status,details = device_obj.get_tui_info()
            table.add_row(name , status, details)
        elif isinstance(device_obj, heater):
            table.add_columns("Device","Status","Power")
            name = device_dict['name']
            status,details = device_obj.get_tui_info()
            table.add_row(name, status, details)
        elif isinstance(device_obj, lock):
            table.add_columns("Device", "Status","Door_state","Battery")
            name = device_dict['name']
            status,door_state, battery = device_obj.get_tui_info()
            table.add_row(name, status, door_state, battery)
        elif isinstance(device_obj, presence_sensor):
            table.add_columns("Device","Status","Presence")
            name = device_dict['name']
            status,presence = device_obj.get_tui_info()
            table.add_row(name,status,presence)
        elif isinstance(device_obj, smart_bulb):
            table.add_columns("Devices","Status","Led")
            name = device_dict['name']
            status,led = device_obj.get_tui_info()
            table.add_row(name,status,led)
        elif isinstance(device_obj, smart_ir):
            table.add_columns("Device","Status")
            name = device_dict['name']
            status = device_obj.get_tui_info()
            table.add_row(name,status)
        elif isinstance(device_obj, smart_lock):
            table.add_columns("Device","Status","Battery", "Lock")
            name = device_dict['name']
            status,battery,state = device_obj.get_tui_info()
            table.add_row(name,status,battery,state)
        elif isinstance(device_obj, smart_plug):
            table.add_columns("Device","Status","State")
            name = device_dict['name']
            status,state = device_obj.get_tui_info()
            table.add_row(name,status,state)
        elif isinstance(device_obj, smart_tv):
            table.add_columns("Device","Status","Power")
            name = device_dict['name']
            status,power = device_obj.get_tui_info()
            table.add_row(name,status,power)
        else:
            table.add_columns("Device","Status")
            name = device_dict['name'] 
            status = "[bold white]Unreacheble[/]"
            table.add_row(name,status)
            
        # 2. NOW disable the UI clutter after the table has structure
        table.show_cursor = False
        table.show_row_labels = False
        # Only show header if you actually want it for every small table
        table.show_header = True
            
        return table
            
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        devices = main.load_devices()
        time.sleep(3)  
        my_devices, my_outside_devices = main.organize_devices(devices)
        floor_data = my_devices.get("Floors",[])
        with Horizontal():
            ##uma coluna por cada andar, e cada andar tem uma tabela com os dispositivos daquele andar
            for index, floor in enumerate(floor_data):
                with Vertical():
                    yield Label(f"Andar:{index}")
                    for index, room in enumerate(floor):
                                yield Label(f"Quarto:{index+1}")
                                for device_dict, device_obj in zip(room.get("Devices",[]), room.get("Objects",[])):
                                    table = DataTable() ## criamos a tabela por quarto
                                    table = self.build_table(table,device_obj,device_dict)                                   
                                    yield table  

            ## 2. Criar uma tabela para os dispositivos "outside"
            with Vertical():
                yield Label("OUTSIDE")
                for device_dict, device_obj in zip(my_outside_devices.get("Devices",[]),my_outside_devices.get("Objects",[])):
                    out_table = DataTable()
                    self.build_table(out_table,device_obj, device_dict)
                    yield out_table
        
if __name__ == "__main__":
    TuyaDashboard().run()
