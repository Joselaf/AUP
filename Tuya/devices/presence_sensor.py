import tinytuya
from is_device_rechable import is_device_reachable

class presence_sensor:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.status = self.device.status()
        self.dps = self.status.get('dps', {})

        self.stats = {
            "presence_status":  self.dps.get('1'),
            "motion_state":     self.dps.get('105'),
            "illuminance_lux":  self.dps.get('104'),
            "target_distance":  self.dps.get('9'),
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

    
    def get_tui_info(self):
        status = "🟢[bold green]ONLINE[/]" if is_device_reachable(self.ip) else "🔴[bold red]OFFLINE[/]"
        details = "[bold yellow]Detected[/]" if self.stats['presence_status'] else "[bold blue]Undetected[/]"
        return status,details



    ## Exercise classification: none, presence, peaceful, small_move, large_move
    def set_motion_state(self, value):
        self.device.set_dps('105', value)
        self.motion_state = value

    def toogle_indicator_switch(self):
        new_state = not self.dps.get('105')
        self.device.set_dps('105', new_state)


