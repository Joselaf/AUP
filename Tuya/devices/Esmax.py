import tinytuya
from is_device_reachable import is_device_reachable

class Esmax:
    def __init__(self, d_id, d_ip, d_local_key, d_name,d_version):
        self.id = d_id
        self.ip = d_ip
        self.key = d_local_key
        self.name = d_name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.key)
        self.device.set_version(d_version)
        self.dps = {}
        self.stats = {}
        self.refresh()
        
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
        _state_lock = None
        _battery = None
        if is_device_reachable(self.ip):
            _status = "🟢 [bold green]ONLINE[/]"
            _state_lock =  "[bold yellow]Locked[/]" if self.stats['switch_lock'] else "[bold blue]Unlocked[/]"
            _battery = f"[bold white]{self.stats['battery']}[/]"
        else:
            _status = "🔴 [bold red]OFFLINE[/]"
            _state_lock = "[bold white]-[/]"
            _battery = "[bold white]-[/]"
            
        table.add_columns("Device", "Status", "Lock State", "Battery")
        table.add_row(name, _status, _state_lock, _battery)

    def get_alerts(self):
        _alerts = []
        _fault = self.stats.get('fault')
        _battery = self.stats.get('battery')
        if _battery is not None and _battery < 20:
            _alerts.append(("BATTERY LOW"))
        elif _fault and str(_fault) != '0':
            _alerts.append((f"VEHICLE FAULT:reported fault code {_fault}!"))
        return _alerts

    def refresh(self):
        status = self.device.status()
        self.dps = status.get('dps', {}) if status else {}
        self.stats = {
            "switch_lock": self.dps.get('1'),
            "gear":        self.dps.get('2'),
            "lights":      self.dps.get('3'),
            "cruise":      self.dps.get('4'),
            "start_mode":  self.dps.get('5'),
            "speed":       self.dps.get('101'),
            "battery":     self.dps.get('102'),
            "mileage":     self.dps.get('103'),
            "trip":        self.dps.get('104'),
            "fault":       self.dps.get('105'),
        }

    def update_from_dps(self, dps: dict) -> None:
        """Called by UDPListener when a broadcast packet arrives for this device."""
        self.dps.update(dps)
        self.stats = {
            "switch_lock": self.dps.get('1'),
            "gear":        self.dps.get('2'),
            "lights":      self.dps.get('3'),
            "cruise":      self.dps.get('4'),
            "start_mode":  self.dps.get('5'),
            "speed":       self.dps.get('101'),
            "battery":     self.dps.get('102'),
            "mileage":     self.dps.get('103'),
            "trip":        self.dps.get('104'),
            "fault":       self.dps.get('105'),
        }

    ## Electronic Lock toggle
    def toogle_switch_lock(self):
        new_state = not self.dps.get('1')
        self.device.set_dps('1', new_state)

    ## Speed Gear: 1=Eco, 2=Normal, 3=Sport
    def set_gear_set(self, value):
        self.device.set_dps('2', value)
        self.gear_set = value

    ## Headlight
    def set_light_switch(self, value):
        self.device.set_dps('3', value)
        self.light_switch = value

    ## Cruise Mode
    def set_cruise_control(self, value):
        self.device.set_dps('4', value)
        self.cruise_control = value

    ## Start Mode: zero or non_zero
    def set_start_mode(self, value):
        self.device.set_dps('5', value)
        self.start_mode = value
