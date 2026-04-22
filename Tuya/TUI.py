from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label
from textual.containers import Horizontal, Vertical
import main
from devices import *
import time

class TuyaDashboard(App):
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        devices = main.load_devices()
        my_devices, my_outside_devices = main.organize_devices(devices)
        
        
        print("Finished loading")
        time.sleep(3)
        floor_data = my_devices.get("Floors",[])
        
        with Horizontal():
            ##uma coluna por cada andar, e cada andar tem uma tabela com os dispositivos daquele andar
            for index, floor in enumerate(floor_data):
                with Vertical():
                    yield Label(f"Andar{index}")
                    table = DataTable(id="device_by_floor") ## criamos a tabela
                    table.add_columns("Device", "Status")
                    for room in floor:
                        for in (room.get("Devices",[], "Objects", [])):
                            status = "[bold green]ONLINE[/]" if device['ip'] else "[bold red]OFFLINE[/]"
                            table.add_row(device['name'], status)
                    yield table

            # 2. Criar uma tabela para os dispositivos "outside"
            with Vertical():
                yield Label("OUTSIDE")
                out_table = DataTable(id="outside_table")
                out_table.add_columns("Device", "Status")
                for device in my_outside_devices:
                    status = "[bold green]ONLINE[/]" if device.get_ip()  else "[bold red]OFFLINE[/]"
                    out_table.add_row(device['name'], status)
                yield out_table

        yield Footer()

if __name__ == "__main__":
    app = TuyaDashboard()
    app.run()
