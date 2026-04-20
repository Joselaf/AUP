from textual.app import App
from textual.widgets import Header, Footer, Static
import main

class TuyaDashboard(App):
    def compose(self):
        yield Header()
        yield Static("Monitoring...!")
        yield Footer()
    
    def load_data(self):
        devices = main.load_devices()
        my_devices, my_outside_devices = main.organize_devices(devices)
        
        
        
        
        
        

if __name__ == "__main__":
    TuyaDashboard().run()