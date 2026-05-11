import tinytuya
from is_device_reachable import is_device_reachable

class Smart_bulb:
    def __init__(self,d_id,d_ip,d_local_key,d_name,d_version):
        self.id = d_id
        self.ip = d_ip
        self.local_key = d_local_key
        self.name = d_name
        self.device = tinytuya.OutletDevice(self.id,self.ip,self.local_key)
        self.device.set_version(d_version)
        self.status = self.device.status()
        if self.status is not None:
             self.dps = self.status.get('dps', {})
        else:
            self.dps = {}

        self.stats = {
            "state":       self.dps.get('20'),
            "mode":        self.dps.get('21'),
            "brightness":  self.dps.get('22'),
            "temperature": self.dps.get('23'),
            "colour":      self.dps.get('24'),
            "scene":       self.dps.get('25'),
            "countdown":   self.dps.get('26'),
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
        _status = None
        _led = None
        if is_device_reachable(self.ip):
            _status = "🟢 [bold green]ONLINE[/]"
            _led = "[bold yellow]ON[/]" if self.stats['led'] else "[bold blue]OFF[/]"
        else:
            _status = "🔴 [bold red]OFFLINE[/]"
            _led = "[bold white]-[/]"
        table.add_columns("Device", "_Status", "_LED")
        table.add_row(name, _status, _led)
    
    def get_alerts(self):
        _alerts = []
        if self.stats.get('state') == False:
            _alerts.append("POWER OFF")
        return _alerts
        
    def refresh(self):
        self.status = self.device.status()
        if self.status is not None:
            self.dps = self.status.get('dps', {})
        else:
            self.dps = {}
        self.stats = {
            "state":       self.dps.get('20'),
            "mode":        self.dps.get('21'),
            "brightness":  self.dps.get('22'),
            "temperature": self.dps.get('23'),
            "colour":      self.dps.get('24'),
            "scene":       self.dps.get('25'),
            "countdown":   self.dps.get('26'),
        }

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
