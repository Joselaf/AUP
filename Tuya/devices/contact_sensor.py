import tinytuya
from is_device_reachable import is_device_reachable

class contact_sensor:
    def __init__(self, d_id, d_ip, d_local_key, d_name,d_version):
        self.id = d_id
        self.ip = d_ip
        self.local_key = d_local_key
        self.name = d_name
        self.device = tinytuya.OutletDevice(d_id,d_ip,D_local_key)
        self.device.set_version(d_version)
        self.status = self.device.status()
        if self.status is not None:
             self.dps = self.status.get('dps', {})
        else:
            self.dps = {}

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
        
    def get_name(self):
        return self.name    

    def get_ip(self):
        return self.ip

    def get_tui_table(self,table,name):
        status = None
        door_state = None
        battery = None
        if is_device_reachable(self.ip):
            status = "🟢 [bold green]ONLINE[/]"
            door_state =  "[bold yellow]Opened[/]" if self.stats['door_state'] else "[bold blue]closed[/]"
            battery = status.get("battery_percentage", status.get("battery_level", status.get("battery")))
        else:      
            status = "🔴 [bold red]OFFLINE[/]"
            door_state = "[bold white]-[/]"
            battery = "[bold white]-[/]"
        table.add_columns("Device", "Status", "Door_State", "Battery")
        table.add_row(name, status, door_state, battery)