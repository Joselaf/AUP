from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label
from textual.containers import Horizontal, Vertical
import main
from devices import *

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
                    yield Label(f"Andar{index}")
                    for room in floor:
                            for device_dict, device_obj in zip(room.get("Devices",[]), room.get("Objects",[])):
                                with Vertical():
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

        yield Footer()

if __name__ == "__main__":
    TuyaDashboard().run()
