import tinytuya

class smart_bulb:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(id, ip, local_key)
        self.dps = self.device.status('dps',{})
        self.refresh_stats()
        
        self.stats:{
            "id":self.id,
            "address:":self.ip, 
            "name":self.name,
            "state":self.dps.get('20'),##True is ON False is OFF
            "mode":self.dps.get('21'),##Modes : white(White Light), colour(Color), scene(Scene), music(Music)
            "brightness":self.dps.get('22'),##White light brightness : typically ranging from 10 to 1000
            "temperature":self.dps.get('23'),##Color temperature range: 0–1000 (0 for warm light, 1000 for cool white)
            "colour":self.dps.get('24'),##RGB Data: Hex string in HSV format (e.g., 000003e803e8)
            "scene":self.dps.get('25'),##Scene data : Preset blinking or fade pattern data
            "countdown":self.dps.get('26'),##Countdown to switch state in seconds (0-86400)
        }
    
    ##Turns the device ON if it is OFF and vice-versa
    def Toogle(self):
        new_state = not self.dps.get('20')
        self.device.set_dps(new_state, '20')

    ##Modes : white(White Light), colour(Color), scene(Scene), music(Music)
    def set_mode(self, value):
        self.device.dps_set(value, '21')

    ##White light brightness : typically ranging from 10 to 1000.
    def set_brightness(self, value):
        self.device.dps_set(value, '22')
    

    ##Color temperature range: 0–1000 (0 for warm light, 1000 for cool white)
    def set_temperature(self, value):
        self.device.dps_set(value, '23')

    ##Colored data : Hexadecimal strings in HSV format (e.g. 000003e803e8)
    def set_colour(self, value):
        self.device.dps_set(value, '24')

    ##Scene data : Preset blinking or fade pattern data
    def set_scene(self, value):
        self.device.dps_set(value, '25')

    ##Countdown to switch state in seconds (0-86400).
    def set_countdown(self, value):
        self.device.dps_set(value, '26')    
    


