import tinytuya

class contact_sensor:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.status = self.device.status()
        self.dps = self.status.get('dps', {})

        self.stats = {
            "door_state":         self.dps.get('1'),   ## True=open, False=closed
            "battery_percentage": self.dps.get('2'),
            "battery_state":      self.dps.get('3'),   ## low / middle / high
            "tamper_alarm":       self.dps.get('4'),   ## True=tampered
        }

    def get_status(self):
        if(self.ip):
            return self.stats
        else:
            return None
    

    def get_ip(self):
        return self.ip

    def get_tui_info(self):
        return "[bold yellow]Opened[/]" if self.stats['door_state'] else "[bold blue]closed[/]"