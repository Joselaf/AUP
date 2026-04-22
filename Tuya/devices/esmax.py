import tinytuya

class esmax:
    def __init__(self, id, ip, key, name):
        self.id = id
        self.ip = ip
        self.key = key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.key)
        self.status = self.device.status()
        self.dps = self.status.get('dps', {})
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
    
    def get_tui_info(self):
         return "[bold yellow]Locked[/]" if self.stats['switch_lock'] else "[bold blue]Unlocked[/]"

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
