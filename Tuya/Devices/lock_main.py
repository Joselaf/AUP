class lock_main:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.refresh_stats(self)
        
    def refresh_stats(self):
        self.dps = self.device.status('dps',{})
        self.feed_status = self.dps('101')
        self.battery = self.dps('102')
        self.pir_switch = self.dps('103')
        self.pir_sensitivity = self.dps('104')
        self.sd_status = self.dps('105')
        self.p2p_id = self.dps('108')
        self.video_flip = self.dps('115')
        self.night_mode = self.dps('116')
