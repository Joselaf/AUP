import tinytuya
from is_device_reachable import is_device_reachable
class Smart_plug:
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
            "state":        self.dps.get('1'),
            "countdown":    self.dps.get('9'),
            "relay_status": self.dps.get('38'),
            "child_lock":   self.dps.get('40'),
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
        _state = None
        if is_device_reachable(self.ip):
            _status = "🟢 [bold green]ONLINE[/]"
            _state = "[bold white]ON[/]" if self.stats['state'] else "[bold white]OFF[/]"
        else:
            _status = "🔴 [bold red]OFFLINE[/]"
            _state = "[bold white]-[/]"
        table.add_columns("Device", "_Status", "_State")
        table.add_row(name, _status, _state)
    
    def get_alerts(self):
        _alerts = []
        _state = self.stats.get('state')
        if _state in (False, 0, "0") or str(_state).strip().lower() in {"false", "off", "no", "none"}:
            _alerts.append(("POWER OFF"))
        return _alerts
            
    def refresh(self):
        self.status = self.device.status()
        if self.status is not None:
            self.dps = self.status.get('dps', {})
        else:
            self.dps = {}
        self.stats = {
            "state":        self.dps.get('1'),
            "countdown":    self.dps.get('9'),
            "relay_status": self.dps.get('38'),
            "child_lock":   self.dps.get('40'),
        }

    def update_from_dps(self, dps: dict) -> None:
        """Called by UDPListener when a broadcast packet arrives for this device."""
        self.dps.update(dps)
        self.stats = {
            "state":        self.dps.get('1'),
            "countdown":    self.dps.get('9'),
            "relay_status": self.dps.get('38'),
            "child_lock":   self.dps.get('40'),
        }

    ## Turns the device ON if it is OFF and vice-versa
    def Toogle(self):
        new_state = not self.dps.get('1')
        self.device.set_dps('1', new_state)

    ## Countdown Timer: Remaining time in seconds before auto-off.
    def set_countdown(self, value):
        self.device.set_dps('9', value)
        self.countdown = value

    ## Power-on State: What the plug does after a power cut (on, off, or memory).
    def set_relay_status(self, value):
        self.device.set_dps('38', value)
        self.relay_status = value

    ## Child Lock: Disables the physical button on the plug.
    def set_child_lock(self, value):
        self.device.set_dps('40', value)
        self.child_lock = value
