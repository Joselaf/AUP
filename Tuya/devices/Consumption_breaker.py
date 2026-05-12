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
            "state": self.dps.get('1'),
            "amps": self.amps,
            "watts": self.watts,
            "volts": self.volts,
            "error": self.dps.get('26'),
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
        _error = None
        _state = None
        if is_device_reachable(self.ip):
            _status = "🟢 [bold green]ONLINE[/]"
            _state = "[bold white]On[/]" if self.stats['state'] == True else "[bold white]OFF[/]"
            _error = "[bold white]None[/]" if self.stats['error'] == 0 else f"[bold white]{breaker_code(self.stats['error'])}[/]"
        else:
            _status = "🔴 [bold red]OFFLINE[/]"
            _state = "[bold white]-[/]"  
            _error = "[bold white]-[/]"
        
        table.add_columns("Device", "Status", "State", "Error")
        table.add_row(name, _status, _state, _error)
        
    def get_alerts(self):
        _alerts = []
        _error = self.stats.get('error')
        _state = self.stats.get('state')
        if _state is not None and _state == False:
            _alerts.append((f"POWER OFF"))
        if _error not in (None, 0, "None"):
            _alerts.append((f"BREAKER ERROR:{breaker_code(self.stats['error'])}!"))
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
            "state": self.dps.get('1'),
            "amps": self.amps,
            "watts": self.watts,
            "volts": self.volts,
            "error": self.dps.get('26'),
            "relay_status": self.dps.get('38'),
            "child_lock": self.dps.get('40')
        }
        self.stats = {
            "state": self.dps.get('1'),
            "amps": self.amps,
            "watts": self.watts,
            "volts": self.volts,
            "error": self.dps.get('26'),
            "relay_status": self.dps.get('38'),
            "child_lock": self.dps.get('40')
        }

    def get_ip(self):
        return self.ip
    
    def get_name(self):
        return self.name   
        
    
    ##Turns the device ON if it is OFF and vice-versa
    def toggle(self):
       new_state = not self.dps.get('1')
       self.device.set_dps('1', new_state)



    ##power_on / power_off / memory
    def set_relay_status(self, value):
        self.device.set_dps('38', value)
        self.relay_status = value



        ##Child Lock: Disables the physical button on the plug.
    def set_childlock(self):
        new_state = not self.child_lock
        self.device.set_dps('40', new_state)
        self.child_lock = new_state
            
    
