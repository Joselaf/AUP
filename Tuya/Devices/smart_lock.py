import tinytuya

class smart_lock:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.dps = self.device.status('dps',{})
        self.refresh_stats(self)

     ##refreshs the stats from the device 
    def refresh_stats(self):
        self.feed_status = self.dps('101')
        self.battery = self.dps('102')
        self.pir_switch = self.dps('103')
        self.pir_sensitivity = self.dps('104')
        self.sd_status = self.dps('105')
        self.p2p_id = self.dps('108')
        self.video_flip = self.dps('115')
        self.night_mode = self.dps('116')

    ##returns the device name
    def get_name():
        return self.name

    ##retuns the device id
    def get_id():
        return self.id

    ##retuns the device ip
    def get_ip():
        return self.ip


    ##Doorbell Call: true when someone rings the bell.
    def get_feed_status():
        return self.feed_status
    
    ##returns Battery Level: 0-100%
    def get_battery():
        return self.battery

    ##PIR Master: Turn motion detection On/Off.
    def set_pir_switch(state):
        new_state = state
        self.device.set_dps(state, '103')
        self.pir_switch = new_state

    ##returns if the motion detection is ON/OFF    
    def get_pir_switch():
        return self.pir_switch
        
    ##returnsPIR Sensitivity 
    def get_pir_sensitivity():
        return self.pir_sensitivity
        
    #PIR Level: low, medium, or high.
    def set_pir_sensitivity(sense):
        self.device.set_dps(sense, '104')
        self.pir_sensitivity = sense

    ## returns SD Card status: normal, error, formatting, or none.
    def get_sd_status(state):
        return self.sd_status
    
    ##returns Stream ID: Used by the app to find the video feed.
    def get_p2p_id():
        return self.p2p_id
    
    ##returns if the video is flipped.
    def get_video_flip():
        return self.video_flip

    ##sets the video flip true or false.
    def set_video_flip(value):
        self.device.set_dps(value, '115')
        self.video_flip = value

    ##Night Mode: 0 = Auto, 1 = On, 2 = Off
    def get_night_mode():
        return self.night_mode

    ##sets the night mode to 0, 1, or 2.
    def set_nighgt_mode(value):
        self.device.set_dps(value, '116')
        self.night_mode = value





