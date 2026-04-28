import tinytuya
from is_device_reachable import is_device_reachable

class smart_bulb:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(id, ip, local_key)
        self.status = self.device.status()
        self.dps = self.status.get('dps', {})
        self.refresh_stats()

    def refresh_stats(self):
        self.led      = self.dps.get('20')
        self.mode     = self.dps.get('21')
        self.bright   = self.dps.get('22')
        self.temp     = self.dps.get('23')
        self.colour   = self.dps.get('24')
        self.scene    = self.dps.get('25')
        self.countdown= self.dps.get('26')

        self.stats = {
            "state":       self.led,
            "mode":        self.mode,
            "brightness":  self.bright,
            "temperature": self.temp,
            "colour":      self.colour,
            "scene":       self.scene,
            "countdown":   self.countdown,
        }
        
    def get_status(self):
        if(self.ip):
            return self.stats
        else:
            return None
       
    def get_ip(self):
        return self.ip
    def get_name(self):
        return self.name
    
    def get_tui_table(self,table,name):
        status = None
        led = None
        if is_device_reachable(self.ip):
            status = "🟢 [bold green]ONLINE[/]"
            led = "[bold yellow]ON[/]" if self.stats['led'] else "[bold blue]OFF[/]"
        else:
            status = "🔴 [bold red]OFFLINE[/]"
            led = "[bold white]-[/]"
        table.add_columns("Device", "Status", "LED")
        table.add_row(name, status, led)
        
    ## Turns the device ON if it is OFF and vice-versa
    def Toogle(self):
        new_state = not self.dps.get('20')
        self.device.set_dps(new_state, '20')

    ## Modes: white, colour, scene, music
    def set_mode(self, value):
        self.device.dps_set(value, '21')

    ## White light brightness: 10-1000
    def set_brightness(self, value):
        self.device.dps_set(value, '22')

    ## Color temperature: 0-1000
    def set_temperature(self, value):
        self.device.dps_set(value, '23')

    ## Colour in HSV hex format
    def set_colour(self, value):
        self.device.dps_set(value, '24')

    ## Scene preset data
    def set_scene(self, value):
        self.device.dps_set(value, '25')

    ## Countdown in seconds (0-86400)
    def set_countdown(self, value):
        self.device.dps_set(value, '26')
