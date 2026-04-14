import tinytuya

class presence_sensor:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.dps = self.device.status('dps',{})
        self.motion_state = None
        self.refresh_stats()

    ##refreshs the stats from the device
    def refresh_stats(self):
        self.presence_status = self.dps.get('1')

    ##returns the device id
    def get_id(self):
        return self.id

    ##returns the device name
    def get_name(self):
        return self.name

    ##returns the device ip
    def get_ip(self):
        return self.ip

    ##Reports the presence status of the sensor (True for detected, False for not detected).
    def get_presence_status(self):
        return self.presence_status
    
    ##Exercise classification : none( rest/breathing), presence( micromotion), (amplitude of motion)peaceful small_move large_move
    def set_motion_state(self, value):
        self.device.set_dps('105', value)
        self.motion_state = value
    
    def get_motion_state(self):
        return self.motion_state
    
    
    def get_illuminance_lux(self):
        return self.dps.get('104')
    
    def get_target_distance(self):
        return self.dps.get('9')
    
    def set_indicator_switch(self, value):
        self.device.set_dps('105', value)
    
    