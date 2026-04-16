import tinytuya

class presence_sensor:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.dps = self.device.status('dps',{})
        
        self.stats:{
            "id":self.id,
            "address:":self.ip, 
            "name":self.name,
            "presence_status":self.dps.get('1'),##Reports the presence status of the sensor (True for detected, False for not detected).
            "motion_state":self.dps.get('105'),## none( rest/breathing), presence( micromotion), (amplitude of motion)peaceful small_move large_move
            "illuminance_lux":self.dps.get('104'),##measurement of ambient light intensity
            "target_distance":self.dps.get('9'),##distance to target
            "indicator_switch":self.dps.get('105'),##if deteted light lights up
            
        }

        def get_status():
            return self.stats
    ##Exercise classification : none( rest/breathing), presence( micromotion), (amplitude of motion)peaceful small_move large_move
    def set_motion_state(self, value):
        self.device.set_dps('105', value)
        self.motion_state = value
    
    def toogle_indicator_switch(self):
        new_state = not self.dps.get('105')
        self.device.set_dps('105', new_state)
    
    