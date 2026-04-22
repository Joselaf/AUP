import tinytuya

class smart_lock:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.status = self.device.status()
        self.dps = self.status.get('dps', {})
        

        self.stats = {
            "battery":         self.dps.get('102'),
            "pir_switch":      self.dps.get('103'),
            "pir_sensitivity": self.pir_sensitivity,
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
    
    def get_tui_info(self):
        return "[bold yellow]Opened[/]" if self.stats['door_state'] else "[bold blue]Closed[/]"
            
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
