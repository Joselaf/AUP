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

    ##refreshs the stats from the device
    def refresh_stats(self):
        self.led = self.dps.get('20')
        self.mode = self.dps.get('21')
        self.bright = self.dps.get('22')
        self.temp = self.dps.get('23')
        self.colour = self.dps.get('24')
        self.scene = self.dps.get('25')
        self.countdown = self.dps.get('26')

        ##returns the device name
        def get_name(self):
            return(self.name)

        ##returns the device id
        def  get_id(self):
            return(self.id)

        ##returns the device ip
        def get_ip(self):
            return(self.ip)

    
    ##Turns the device ON if it is OFF and vice-versa
    def Toogle(self):
        new_state = not self.led
        self.device.set_dps(new_state, '1')
        self.led = new_state

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

    ##Countdown : in seconds (0–86400)
    def set_countdown(self, value):
        self.device.dps_set(value, '26')
        
    def get_state(self):
        return self.led

    def get_mode(self):
        return self.mode
    
    def get_brightness(self):
        return self.bright
    
    def get_temperature(self):
        return self.temp
    
    def get_colour(self):
        return self.colour
    
    def get_scene(self):
        return self.scene
    
    def get_countdown(self):
        return self.countdown
    


