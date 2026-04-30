import tinytuya
from is_device_reachable import is_device_reachable
class lock:
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
            "finger_unlocked":    self.dps.get('1'),   ## ID of fingerprint used
            "password_unlocked":  self.dps.get('2'),   ## ID of local password used
            "password_generated": self.dps.get('3'),   ## App-generated temp code
            "card_unlocked":      self.dps.get('5'),   ## RFID card/tag ID
            "key":                self.dps.get('7'),   ## Physical key used
            "door_status":        self.dps.get('8'),   ## True=open, False=closed
            "alarms":             self.dps.get('9'),   ## wrong_password, low_battery, etc.
            "battery_level":      self.dps.get('10'),  ## 0-100%
            "doorbell":           self.dps.get('14'),  ## True when doorbell pressed
            "remote":             self.dps.get('61'),  ## True if opened remotely
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
        door_state = None
        battery = None
        door_state =  "[bold yellow]Opened[/]" if self.stats['door_status'] else "[bold blue]Closed[/]"
        battery = self.stats.get("battery_percentage", self.stats.get("battery_level", self.stats.get("battery")))
        status = "🔴 [bold red]OFFLINE[/]"
            
        table.add_columns("Device", "Status", "Door State", "Battery")
        table.add_row(name, status, door_state, battery)
