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
            "switch_lock": self.switch_lock,   ## True=Locked, False=Unlocked
            "gear":        self.gear_set,       ## 1=Eco, 2=Normal, 3=Sport
            "lights":      self.light_switch,
            "cruise":      self.cruise_control,
            "start_mode":  self.start_mode,
            "speed":       self.speed,          ## in 0.1 km/h units
            "battery":     self.battery_level,  ## 0-100%
            "mileage":     self.milage,
            "trip":        self.milage_trip,
            "fault":       self.fault,
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
        state_lock = None
        battery = None
        if is_device_reachable(self.ip):
            status = "🟢[bold green]ONLINE[/]"
            state_lock =  "[bold yellow]Locked[/]" if self.stats['switch_lock'] else "[bold blue]Unlocked[/]"
            battery = f"[bold white]{self.stats['battery']}[/]"
        else:
            status = "🔴[bold red]OFFLINE[/]"
            state_lock = "[bold white]-[/]"
            battery = "[bold white]-[/]"
            
        table.add_columns("Device", "Status", "Lock State", "Battery")
        table.add_row(name, status, state_lock, battery)

    def get_alerts(self):
        _alerts = []
        _fault = self.stats.get('fault')
        _battery = self.stats.get('battery')
        if _battery is not None and _battery < 20:
            _alerts.append(("BATTERY LOW"))
        elif _fault and str(_fault) != '0':
            _alerts.append((f"VEHICLE FAULT:reported fault code {_fault}!"))
        return _alerts
    
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
