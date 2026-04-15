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
        
        ##It return the status of the device
        self.stats:{
            "id":self.id,
            "address:":self.ip, 
            "name":self.name,
            "switch":self.dps.get('1'),##Electronic Lock: true (Locked), false (Unlocked)
            "gear":self.dps.get('2'),##Speed Gear: Usually 1 (Eco), 2 (Normal), 3 (Sport)
            "light":self.dps.get('3'),##Headlight: Controls the front and rear LEDs
            "cruise":self.dps.get('4'),##Cruise Mode: Toggles auto-throttle assistance
            "start":self.dps.get('5'),##Start Mode: zero (Static start), non_zero (Kick-to-start)
            "speed":self.dps.get('101'),##Speed in km/h
            "battery":self.dps.get('102'),##0-100%
            "milage":self.dps.get('103'),## quilometragem total
            "milage_trip":self.dps.get('104'),##quilometragem da viagem
            "fault":self.dps.get('105'),##Fault Code: 0 (No Faults)
        }
        
    
    
    def set_switch_lock(self, value):
        self.device.set_dps('1', value)
        self.switch_lock = value
        
 
    def set_gear_set(self, value):
        self.device.set_dps('2', value)
        self.gear_set = value
        
    def set_light_switch(self, value):
        self.device.set_dps('3', value)
        self.light_switch = value
        
   
    def set_cruise_control(self, value):
        self.device.set_dps('4', value)
        self.cruise_control = value
        

    def set_start_mode(self, value):
        self.device.set_dps('5', value)
        self.start_mode = value