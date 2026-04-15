import tinytuya

class contact_sensor:
        def __init__(self, id, ip, local_key, name):
            self.id = id
            self.ip = ip
            self.local_key = local_key
            self.name = name
            self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
            self.dps = self.device.status('dps',{})

            ##It return the status of the device
            self.stats = {
            "id": self.id,
            "address:":self.ip, 
            "name":self.name,
            "door_state":self.dps.get('1'), ##open/close
            "battery_percentage":self.dps.get('2'),
            "battery_state":self.dps.get('3'), ##low/mid/high
            "tamper_alarm":self.dps.get('4'), ##true/false
            }

    



        
        
