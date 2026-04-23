from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label
from textual.containers import Horizontal, Vertical
import main
from devices import *

class TuyaDashboard(App):
    
        
    def build_table(self, table, device_obj, device_dict):
        if device_obj == breaker or consumption_breaker:
            table.add_columns("Device", "Status","State","Error")
            name = device_dict['name']
            status,state,details = device_obj.get_tui_info()
            table.add_row(name,status,state,details)
        elif device_obj == contact_sensor:
            table.add_column("Device", "Status","Door_state","Battery")
            name = device_dict['name']
            status,door_state, battery = device_obj.get_tui_info()
            table.add_row(name, status, door_state, battery)
        elif device_obj == esmax:
            table.add_column("Device", "Status","State_Lock","Battery")
            name = device_dict['name']
            status,state_lock,battery = device_obj.get_tui_info()
            table.add_row(name, status, state_lock, battery)
        elif device_obj == general_circuit_breaker:
            table.add_columns("Device", "Status","State","Error")
            name = device_dict['name']
            status,details = device_obj.get_tui_info()
            table.add_row(name , status, details)
        elif device_obj == heater:
            table.add_column("Device","Status","Power")
            name = device_dict['name']
            status,details = device_obj.get_tui_info()
            table.add_row(name, status, details)
        elif device_obj == lock:
            table.add_column("Device", "Status","Door_state","Battery")
            name = device_dict['name']
            status,door_state, battery = device_obj.get_tui_info()
            table.add_row(name, status, door_state, battery)
        elif device_obj == presence_sensor:
            table.add_column("Device","Status","Presence")
            name = device_dict['name']
            status,presence = device_obj.get_tui_info()
            table.add_row(name,status,presence)
        elif device_obj == smart_bulb:
            table.add_column("Devices","Status","Led")
            name = device_dict['name']
            status,led = device_obj.get_tui_info()
            table.add_row(name,status,led)
        elif device_obj == smart_ir:
            table.add_column("Device","Status")
            name = device_dict['name']
            status = device_obj.get_tui_info()
            table.add_row(name,status)
        elif device_obj == smart_lock:
            table.add_column("Device","Status","Battery", "Lock")
            name = device_dict['name']
            status,battery,state = device_obj.get_tui_info()
            table.add_row(name,status,battery,state)
        elif device_obj == smart_plug:
            table.add_column("Device","Status","Power")
        return table
            
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        devices = main.load_devices()
        my_devices, my_outside_devices = main.organize_devices(devices)
        floor_data = my_devices.get("Floors",[])
        with Horizontal():
            status = None
            details = None
            ##uma coluna por cada andar, e cada andar tem uma tabela com os dispositivos daquele andar
            for index, floor in enumerate(floor_data):
                with Vertical():
                    yield Label(f"Andar{index}")
                    for room in floor:
                        table = DataTable(id="device_by_room") ## criamos a tabela por quarto
                        for device_dict, device_obj in zip(room.get("Devices",[]), room.get("Objects",[])):
                            if(device_obj):
                                table = self.build_table(table, device_obj, device_dict)
                                
                    yield table

            # 2. Criar uma tabela para os dispositivos "outside"
            with Vertical():
                yield Label("OUTSIDE")
                out_table = DataTable(id="outside_table")
                out_table.add_columns("Device", "Status", "Details")
                for device_dict, device_obj in zip(my_outside_devices.get("Devices",[]),my_outside_devices.get("Objects",[])):
                    if device_obj:
                        status = "🟢[bold green]ONLINE[/]"
                        details = device_obj.get_tui_info()
                    else:
                        status = "🔴[bold red]OFFLINE[/]"
                    
                    out_table.add_row(device_dict['name'], status, details)
                yield out_table

        yield Footer()

if __name__ == "__main__":
    TuyaDashboard().run()
