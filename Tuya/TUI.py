from textual.app import App
from textual.widgets import Header, Footer, Static
import main

class HelloWorldApp(App):
    def compose(self):
        yield Header()
        yield Static("Hello, World!")
        yield Footer()
    
    def load_data(self):
        devices = main.load_devices()
        

if __name__ == "__main__":
    HelloWorldApp().run()