import tinytuya

class smart_ir:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(id, ip, local_key)
        self.status = self.device.status()
        self.dps = self.status.get('dps', {})

        self.stats = {
            "id":      self.id,
            "address": self.ip,
        }
        
    def get_status(self):
        if(self.ip):
            return self.stats
        else:
            return None

    def get_ip(self):
        return self.ip
    def get_name(self):
        return self.name
    
    
    
    
    ## Send Code: The raw IR code (Base64) to be emitted.
    def send_ir_code(self, code):
        payload = self.device.generate_payload(tinytuya.CONTROL, {'1': code})
        self.device.send(payload)

    ## Learning Mode: Receives and reports the IR code from a physical remote.
    def enter_learning_mode(self):
        payload = self.device.generate_payload(tinytuya.CONTROL, {'2': True})
        self.device.send(payload)
