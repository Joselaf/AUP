class smart_plug:
     def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(id, ip, local_key)
        self.refresh_stats(self)


     def refresh_stats(self):
        self.dps = self.device.status('dps',{})
        self.state = self.dps('1')
        self.countdown = self.dps('9')
        self.relay_status = self.dps('38')
        self.child_lock = self.dps('40')
        
