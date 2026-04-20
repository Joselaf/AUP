from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Monitoring TUYA devices...")
        
        yield Footer()

if __name__ == "__main__":
    MyApp().run()