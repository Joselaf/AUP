import tinytuya
from is_device_reachable import is_device_reachable
from breaker_code import breaker_code

class Consumption_breaker:
    def __init__(self, d_id, d_ip, d_local_key, d_name, d_version):
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

        # 1. PRE-CALCULATE values with safety checks
        try:
            self.watts = float(self.dps.get('19', 0)) / 10.0
        except (ValueError, TypeError):
            self.watts = 0.0

        try:
            self.amps = float(self.dps.get('18', 0)) / 1000.0
        except (ValueError, TypeError):
            self.amps = 0.0

        try:
            self.volts = float(self.dps.get('20', 0)) / 10.0
        except (ValueError, TypeError):
            self.volts = 0.0

        # 2. DEFINE the dictionary using the pre-calculated values
        self.stats = {
            "state": self._normalize_state(self.dps.get('1')),
            "amps": self.amps,
            "watts": self.watts,
            "volts": self.volts,
            "fault": self.dps.get('26'),
            "relay_status": self.dps.get('38'),
            "child_lock": self.dps.get('40')
        }

    ##It return the status of the device
    def get_status(self):
        if(self.ip):
            return self.stats
        else:
            return None

    def get_tui_table(self,table,name):
        _status = None
        _fault = None
        _state = None
        if is_device_reachable(self.ip):
            _status = "🟢 [bold green]ONLINE[/]"
            _state = "[bold white]On[/]" if self.stats['state'] == True else "[bold white]OFF[/]"
            _fault = "[bold white]None[/]" if self.stats['state'] == True in (None,"None") else f"[bold white]{breaker_code(self.stats['fault'])}[/]"
        else:
            _status = "🔴 [bold red]OFFLINE[/]"
            _state = "[bold white]-[/]"  
            _fault = "[bold white]-[/]"
        
        table.add_columns("Device", "Status", "State", "Fault")
        table.add_row(name, _status, _state, _fault)
        
    def get_alerts(self):
        _alerts = []
        _fault = self.stats.get('fault')
        _state = self.stats.get('state')
        if _state in (False, 0, "0"):
            if _fault is not None:
                _alerts.append(f"Breaker OFF:{breaker_code(_fault)}")
                if self.stats['watts'] == 0 and self.stats['amps'] == 0 and _fault is None:
                    _alerts.append("BREAKER TRIPPED!")
            else:
                _alerts.append("POWER OFF")
        return _alerts

    def refresh(self):
        self.status = self.device.status()
        if self.status is not None:
            self.dps = self.status.get('dps', {})
        else:
            self.dps = {}
        try:
            self.watts = float(self.dps.get('19', 0)) / 10.0
        except (ValueError, TypeError):
            self.watts = 0.0

        try:
            self.amps = float(self.dps.get('18', 0)) / 1000.0
        except (ValueError, TypeError):
            self.amps = 0.0

        try:
            self.volts = float(self.dps.get('20', 0)) / 10.0
        except (ValueError, TypeError):
            self.volts = 0.0

        # Update self.stats with the refreshed values
        self.stats = {
            "state": self._normalize_state(self.dps.get('1')),
            "amps": self.amps,
            "watts": self.watts,
            "volts": self.volts,
            "fault": self.dps.get('26'),
            "relay_status": self.dps.get('38'),
            "child_lock": self.dps.get('40')
        }

    def get_ip(self):
        return self.ip
    
    def get_name(self):
        return self.name   
        
    
    ##Turns the device ON if it is OFF and vice-versa
    def toggle(self):
       new_state = not self._normalize_state(self.dps.get('1'))
       self.device.set_dps('1', new_state)

    def _normalize_state(self, raw_state):
        if isinstance(raw_state, bool):
            return raw_state
        if raw_state in (0, "0", False):
            return False
        if raw_state in (1, "1", True):
            return True
        dp12 = self.dps.get('12')
        if isinstance(dp12, bool):
            return dp12
        if dp12 in (0, "0", False):
            return False
        if dp12 in (1, "1", True):
            return True
        dp16 = self.dps.get('16')
        if isinstance(dp16, bool):
            return dp16
        if dp16 in (0, "0", False):
            return False
        if dp16 in (1, "1", True):
            return True
        return raw_state not in (None, "None", "")



    ##power_on / power_off / memory
    def set_relay_status(self, value):
        self.device.set_dps('38', value)
        self.relay_status = value



        ##Child Lock: Disables the physical button on the plug.
    def set_childlock(self):
        new_state = not self.child_lock
        self.device.set_dps('40', new_state)
        self.child_lock = new_state
            
    
