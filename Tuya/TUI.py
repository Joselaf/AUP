from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label
from textual.containers import Horizontal, Vertical
import main

class TuyaDashboard(App):

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
    
        devices = main.load_devices()
        my_devices, my_outside_devices = main.organize_devices(devices)
        index_floor = 0
        with Horizontal():
            ##uma coluna por cada andar, e cada andar tem uma tabela com os dispositivos daquele andar
            for index, floor in enumerate(my_devices.get("Floors", [])):
                with Vertical():
                    yield Label(f"Andar{index}")
                    table = DataTable() ## criamos a tabela
                    table.add_columns("Device", "Status")
                    index_floor += 1
                    
                    for room in floor:
                        for device in room.get("Devices", []):
                            status = "[bold green]ONLINE[/]" if device.get('ip') else "[bold red]OFFLINE[/]"
                            table.add_row(device['name'], status)
                    yield table

            # 2. Criar uma tabela para os dispositivos "outside"
            with Vertical():
                yield Label("OUTSIDE")
                out_table = DataTable(id="outside-table")
                out_table.add_columns("Device", "Status")
                for device in my_outside_devices:
                    status = "[bold green]ONLINE[/]" if device.get('ip') else "[bold red]OFFLINE[/]"
                    out_table.add_row(device['name'], status)
                yield out_table

        yield Footer()

if __name__ == "__main__":
    app = TuyaDashboard()
    app.run()