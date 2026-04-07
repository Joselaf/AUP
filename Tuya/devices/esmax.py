import tinytuya

class esmax:
    def __init__(self, id, ip, key, name):
        self.id = id
        self.ip = ip
        self.key = key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.key)
        self.dps = self.device.status('dps',{})
        self.switch_lock = self.dps.get('1')
        self.gear_set = self.dps.get('2')
        self.light_switch = self.dps.get('3')
        self.cruise_control = self.dps.get('4')
        self.start_mode = self.dps.get('5')
        self.speed = self.dps.get('101')
        self.battery_level = self.dps.get('102')
        self.milage = self.dps.get('103')
        self.milage_trip = self.dps.get('104')
        self.fault = self.dps.get('105')
        self.refresh_stats()
        
    ##refreshs the stats from the device
    def refresh_stats(self):
        self.switch_lock = self.dps.get('1')
        self.gear_set = self.dps.get('2')
        self.light_switch = self.dps.get('3')
        self.cruise_control = self.dps.get('4')
        self.start_mode = self.dps.get('5')
        self.speed = self.dps.get('101')
        self.battery_level = self.dps.get('102')
        self.milage = self.dps.get('103')
        self.milage_trip = self.dps.get('104')
        self.fault = self.dps.get('105')
    
    
    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name
    def get_ip(self):
        return self.ip
    ##Electronic Lock: true (Locked), false (Unlocked)
    def get_switch_lock(self):
        return self.switch_lock
    def set_switch_lock(self, value):
        self.device.set_dps('1', value)
        self.switch_lock = value
        
    ##Speed Gear: Usually 1 (Eco), 2 (Normal), 3 (Sport).
    def get_gear_set(self):
        return self.gear_set
    def set_gear_set(self, value):
        self.device.set_dps('2', value)
        self.gear_set = value
        
    ##Headlight: Controls the front and rear LEDs.
    def get_light_switch(self):
        return self.light_switch
    def set_light_switch(self, value):
        self.device.set_dps('3', value)
        self.light_switch = value
        
    ##Cruise Mode: Toggles auto-throttle assistance.
    def get_cruise_control(self):
        return self.cruise_control
    def set_cruise_control(self, value):
        self.device.set_dps('4', value)
        self.cruise_control = value
        
    ##Start Mode: zero (Static start), non_zero (Kick-to-start).
    def get_start_mode(self):
        return self.start_mode
    def set_start_mode(self, value):
        self.device.set_dps('5', value)
        self.start_mode = value
        
    ##Current Speed: Usually in 0.1 km/h (e.g., 250 = 25 km/h).
    def get_speed(self):
        return self.speed
    ##Battery Level: Current charge from 0% to 100%.
    def get_battery_level(self):
        return self.battery_level
    
    ##Odometer: Total cumulative distance (Unit: 0.1 km).
    def get_milage(self):
        return self.milage
    
    ##rip Distance: Distance since the last power cycle.
    def get_milage_trip(self):
        return self.milage_trip 