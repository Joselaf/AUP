import tinytuya
from is_device_reachable import is_device_reachable
class smart_lock:
    def __init__(self,d_id,d_ip,d_local_key,d_name,d_version):
        self.id = d_id
        self.ip = d_ip
        self.local_key = d_local_key
        self.name = d_name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.device.set_version(d_version)
        self.status = self.device.status()
        if self.status is not None:
             self.dps = self.status.get('dps', {})
        else:
            self.dps = {}
        

        self.stats = {
            "battery":         self.dps.get('102'),
            "pir_switch":      self.dps.get('103'),
            "pir_sensitivity": self.dps.gte('104'),
            "sd_status":       self.dps.get('105'),
            "video_flip":      self.dps.get('115'),
            "night_mode":      self.dps.get('116'),
            "door_state":      self.dps.get('63'),
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
        battery = None
        door_state = None
        status = "🔴 [bold red]OFFLINE[/]"
        battery = f"[bold white]{self.stats['battery']}"
        door_state = "[bold yellow]Opened[/]" if self.stats['door_state'] else "[bold blue]Closed[/]"

        table.add_columns("Device", "Status", "Battery", "Lock")
        table.add_row(name, status, battery, state)
            
    def set_pir_switch(self, state):
        self.device.set_dps('103', state)
        self.pir_switch = state

    def set_pir_sensitivity(self, sense):
        self.device.set_dps('104', sense)
        self.pir_sensitivity = sense

    def set_video_flip(self, value):
        self.device.set_dps('115', value)
        self.video_flip = value

    def set_night_mode(self, value):
        self.device.set_dps('116', value)
        self.night_mode = value
