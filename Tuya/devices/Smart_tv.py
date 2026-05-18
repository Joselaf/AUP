import tinytuya
from is_device_reachable import is_device_reachable
class Smart_tv:
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
        self.power  = self.dps.get('1')
        self.volume = self.dps.get('2')
        self.mute   = self.dps.get('3')
        self.mode   = self.dps.get('4')
        self.source = self.dps.get('102')

        self.stats = {
            "power":   self.power,
            "volume":  self.volume,
            "mute":    self.mute,
            "mode":    self.mode,
            "source":  self.source,
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
        _power = None
        if is_device_reachable(self.ip):
            _status = "🟢 [bold green]ONLINE[/]"
            _power =    "[bold yellow]ON[/]" if self.stats['power'] else "[bold blue]OFF[/]"
        else:
            _status = "🔴 [bold red]OFFLINE[/]"
            _power =  "[bold white]-[/]"
        table.add_columns("Device", "_Status", "_Power")
        table.add_row(name, _status, _power)
    
    def get_alerts(self):
        return []
            
    def refresh(self):
        self.status = self.device.status()
        if self.status is not None:
            self.dps = self.status.get('dps', {})
        else:
            self.dps = {}
        self.power  = self.dps.get('1')
        self.volume = self.dps.get('2')
        self.mute   = self.dps.get('3')
        self.mode   = self.dps.get('4')
        self.source = self.dps.get('102')
        self.stats = {
            "power":   self.power,
            "volume":  self.volume,
            "mute":    self.mute,
            "mode":    self.mode,
            "source":  self.source,
        }

    def update_from_dps(self, dps: dict) -> None:
        """Called by UDPListener when a broadcast packet arrives for this device."""
        self.dps.update(dps)
        self.power  = self.dps.get('1')
        self.volume = self.dps.get('2')
        self.mute   = self.dps.get('3')
        self.mode   = self.dps.get('4')
        self.source = self.dps.get('102')
        self.stats = {
            "power":   self.power,
            "volume":  self.volume,
            "mute":    self.mute,
            "mode":    self.mode,
            "source":  self.source,
        }

    ## Turns the device ON if it is OFF and vice-versa
    def Toogle(self):
        new_state = not self.dps.get('1')
        self.device.set_dps('1', new_state)

    ## Volume setting: Normal range 0-100
    def set_volume(self, value):
        self.device.dps_set(value, '2')

    ## Turns the mute ON if it is OFF and vice-versa
    def set_mute(self):
        new_state = not self.mute
        self.device.set_dps(new_state, '1')
        self.mute = new_state

    ## Image patterns: such as standard, vivid, movie, user
    def set_mode(self, value):
        self.device.dps_set(value, '4')

    ## Control panel: Simulated remote control up/down/left/right/OK buttons
    def set_tv_pannel(self, value):
        self.device.dps_set(value, '16')

    ## Input source: such as HDMI1, HDMI2, AV, TV, USB
    def set_source(self, value):
        self.device.dps_set(value, '101')
