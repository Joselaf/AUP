import tinytuya

class smart_tv:
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
            "power":self.dps.get('1'),##if the devces is ON or OFF
            "volume":self.dps.get('2'),##Volume atm in the devices
            "mute":self.dps.get('3'),##if the mute is ON or OFF
            "mode":self.dps.get('4'),##Image patterns : such as standard, vivid, movie, user
            "source":self.dps.get('102'),##Input source : such as HDMI1, HDMI2, AV, TV,USB
        }

    ##Turns the device ON if it is OFF and vice-versa
    def Toogle(self):
        new_state = not self.power
        self.device.set_dps(new_state, '1')
        self.power = new_state
    
    ##Volume setting : Normal range 0–100
    def set_volune(self, value):
        self.device.dps_set(value, '2')

    ##Turns the mute ON if it is OFF and vice-versa
    def set_mute(self):
        new_state = not self.mute
        self.device.set_dps(new_state, '1')
        self.mute = new_state
    

    ##mage patterns : such as standard, vivid, movie, user
    def set_mode(self, value):
        self.device.dps_set(value, '4')


    ##Control panel : Simulated remote control up/down/left/right/OK buttons
    def set_tv_pannel(self, value):
        self.device.dps_set(value, '16')
    

    ##Input source : such as HDMI1, HDMI2, AV, TV,USB
    def set_source(self, value):
        self.device.dps_set(value, '101')

        