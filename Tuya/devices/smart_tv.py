import tinytuya
from is_device_reachable import is_device_reachable
class smart_tv:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(id, ip, local_key)
        self.status = self.device.status()
        self.dps = self.status.get('dps', {})
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
        status = None
        power = None
        if is_device_reachable(self.ip):
            status = "🟢 [bold green]ONLINE[/]"
            power =    "[bold yellow]ON[/]" if self.stats['power'] else "[bold blue]OFF[/]"
        else:
            status = "🔴 [bold red]OFFLINE[/]"
            power =  "[old white]-[/]"
        table.add_columns("Device", "Status", "Power")
        table.add_row(name, status, power)
        
        
            
            
    ## Turns the device ON if it is OFF and vice-versa
    def Toogle(self):
        new_state = not self.dps.get('1')
        self.device.set_dps('1', new_state)

    ## Volume setting: Normal range 0-100
    def set_volune(self, value):
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
