from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label
from textual.containers import Horizontal, Vertical
import main
from devices import *

class TuyaDashboard(App):
    
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
                    table = DataTable(id="device_by_floor") ## criamos a tabela
                    table.add_columns("Device", "Status")
                    for room in floor:
                        for device in room.get("Devices", []):
                            status = "[bold green]ONLINE[/]" if device['ip'] else "[bold red]OFFLINE[/]"
                            table.add_row(device['name'], status)
                    yield table

            # 2. Criar uma tabela para os dispositivos "outside"
            with Vertical():
                yield Label("OUTSIDE")
                out_table = DataTable(id="outside_table")
                out_table.add_columns("Device", "Status", "Details")
                for device in my_outside_devices:
                    detail = main.devices_status(device)
                    if detail is not None:
                        details = "[bold yellow]ON[/]" if detail.get('state') else "[bold blue]OFF[/]"
                    else:
                        details = "[bold white]Error[/]"
                    status = "[bold green]ONLINE[/]" if device['ip'] else "[bold red]OFFLINE[/]"
                    out_table.add_row(device['name'], status, details)
                yield out_table

        yield Footer()

if __name__ == "__main__":
    app = TuyaDashboard()
    app.run()
