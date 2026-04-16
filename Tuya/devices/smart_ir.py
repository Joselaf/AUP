import tinytuya

class smart_ir:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(id, ip, local_key)
        self.dps = self.device.status('dps',{})
        
        self.stats:{
            "id":self.id,
            "address:":self.ip, 
            "name":self.name,
        }
        def get_status():
            return self.stats
