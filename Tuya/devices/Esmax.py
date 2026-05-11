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
        self.status = self.device.status()
        if self.status is not None:
             self.dps = self.status.get('dps', {})
        else:
            self.dps = {}
        self.stats = {
            "switch_lock":  self.dps.get('1'),   ## True=Locked, False=Unlocked
            "gear":        self.dps.get('2'),       ## 1=Eco, 2=Normal, 3=Sport
            "lights":      self.dps.get('3'),
            "cruise":      self.dps.get('4'),
            "start_mode":  self.dps.get('5'),
            "speed":       self.dps.get('101'),          ## in 0.1 km/h units
            "battery":     self.dps.get('102'),  ## 0-100%
            "mileage":     self.dps.get('103'),
            "trip":        self.dps.get('103'),
            "fault":       self.dps.get('105')
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
        self.status = self.device.status()
        if self.status is not None:
            self.dps = self.status.get('dps', {})
        else:
            self.dps = {}
        self.switch_lock    = self.dps.get('1')
        self.gear_set       = self.dps.get('2')
        self.light_switch   = self.dps.get('3')
        self.cruise_control = self.dps.get('4')
        self.start_mode     = self.dps.get('5')
        self.speed          = self.dps.get('101')
        self.battery_level  = self.dps.get('102')
        self.milage         = self.dps.get('103')
        self.milage_trip    = self.dps.get('104')
        self.fault          = self.dps.get('105')
        self.stats = {
            "switch_lock": self.switch_lock,
            "gear":        self.gear_set,
            "lights":      self.light_switch,
            "cruise":      self.cruise_control,
            "start_mode":  self.start_mode,
            "speed":       self.speed,
            "battery":     self.battery_level,
            "mileage":     self.milage,
            "trip":        self.milage_trip,
            "fault":       self.fault,
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
