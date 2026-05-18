import tinytuya
from is_device_reachable import is_device_reachable

class Contact_sensor:
    def __init__(self, d_id, d_ip, d_local_key, d_name,d_version):
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
        _status = None
        _door_state = None
        _battery = None
        if is_device_reachable(self.ip):
            _status = "🟢 [bold green]ONLINE[/]"
            _door_state = "[bold yellow]Opened[/]" if self.stats['door_state'] else "[bold blue]Closed[/]"
            _battery = self.stats.get("battery_state")
        else:      
            _status = "🔴 [bold red]OFFLINE[/]"
            _door_state = "[bold white]-[/]"
            _battery = "[bold white]-[/]"
        table.add_columns("Device", "_Status", "Door_State", "Battery")
        table.add_row(name, _status, _door_state, _battery)
    
    def get_alerts(self):
        _alerts = []
        if self.stats.get('tamper_alarm'):
            _alerts.append((f"TAMPER ALERT:detected a tampering attempt!"))
        elif(self.stats['battery_state'] == 'low'):
            _alerts.append(("BATTERY LOW"))
        return _alerts

    def refresh(self):
        self.status = self.device.status()
        if self.status is not None:
            self.dps = self.status.get('dps', {})
        else:
            self.dps = {}
        self.stats = {
            "door_state":         self.dps.get('1'),
            "battery_percentage": self.dps.get('2'),
            "battery_state":      self.dps.get('3'),
            "tamper_alarm":       self.dps.get('4'),
        }

    def update_from_dps(self, dps: dict) -> None:
        """Called by UDPListener when a broadcast packet arrives for this device."""
        self.dps.update(dps)
        self.stats = {
            "door_state":         self.dps.get('1'),
            "battery_percentage": self.dps.get('2'),
            "battery_state":      self.dps.get('3'),
            "tamper_alarm":       self.dps.get('4'),
        }