import tinytuya
from is_device_reachable import is_device_reachable

class Presence_sensor:
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

    
    def get_tui_table(self,table,name):
        _status = None
        _presence = None
        if is_device_reachable(self.ip):
            _status = "🟢 [bold green]ONLINE[/]"
            _presence = "[bold white]Detected[/]" if self.stats['presence_status'] else "[bold white]Undetected[/]"
        else:
            _status = "🔴 [bold red]OFFLINE[/]"
            _presence = "[bold white]-[/]"
        table.add_columns("Device", "_Status", "_Presence")
        table.add_row(name, _status, _presence)
        
    def get_alerts(self):
        _alerts = []
        if self.stats.get('presence_status'):
            _alerts.append(("PRESENCE DETECTED"))
        return _alerts

    def refresh(self):
        self.status = self.device.status()
        if self.status is not None:
            self.dps = self.status.get('dps', {})
        else:
            self.dps = {}
        self.stats = {
            "presence_status":  self.dps.get('1'),
            "motion_state":     self.dps.get('105'),
            "illuminance_lux":  self.dps.get('104'),
            "target_distance":  self.dps.get('9'),
        }

    ## Exercise classification: none, presence, peaceful, small_move, large_move
    def set_motion_state(self, value):
        self.device.set_dps('105', value)
        self.motion_state = value

    def toogle_indicator_switch(self):
        new_state = not self.dps.get('105')
        self.device.set_dps('105', new_state)


