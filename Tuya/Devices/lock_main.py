import tinytuya

class lock_main:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.dps = self.device.status('dps',{})
        self.refresh_stats(self)
        
    def refresh_stats(self):
        self.feed_status = self.dps('101')
        self.battery = self.dps('102')
        self.pir_switch = self.dps('103')
        self.pir_sensitivity = self.dps('104')
        self.sd_status = self.dps('105')
        self.p2p_id = self.dps('108')
        self.video_flip = self.dps('115')
        self.night_mode = self.dps('116')

    def get_feed_status():
        return self.feed_status
    
    def get_battery():
        return self.battery
    
    def get_pir_switch():
        return self.pir_switch

    def get_pir_sensitivity():
        return self.pir_sensitivity
    
    def set_pir_sensitivity(sense):
        self.device.set_dps(sense, '104')
        self.pir_sensitivity = sense

    def get_sd_status():
        return self.sd_status
    
    def get_p2p_id():
        return self.p2p_id
    
    def get_video_flip():
        return self.video_flip

    def set_video_flip(value):
        self.device.set_dps(value, '115')
        self.video_flip = value

    
    def get_night_mode():
        return self.night_mode

    def set_nighgt_mode(value):
        self.device.set_dps(value, '116')
        self.night_mode = value





