import tinytuya

class consumption_breaker:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(id, ip, local_key)
        self.volts = 0.0
        self.amps = 0.0
        self.watts = 0.0
        self.add_ele = 0.0
        self.dps = self.device.status('dps',{})
        self.dps = self.dps.get('dps', self.dps) if isinstance(self.dps, dict) else {}
        
        ##It return the status of the device
        self.stats = {
            "id": self.id,
            "address:":self.ip, 
            "name":self.name,
            "state":self.dps.get('1'),
            "amps":(self.dps.get('18') / 1000.0),
            "watts":(self.dps.get('19') / 10.0),
            "volts":(self.dps.get('20') / 10.0),
            "error":self.dps.get('26'),
            "relay_status":self.dps.get('38'),
            "child_lock":self.dps.get('40')
            }


    def get_status():
        return self.stats
    
    
    ##Turns the device ON if it is OFF and vice-versa
    def toggle(self):
       new_state = not self.dps.get('1')
       self.device.set_dps('1', new_state)



    ##power_on / power_off / memory
    def set_relay_status(self, value):
        self.device.set_dps('38', value)
        self.relay_status = value



        ##Child Lock: Disables the physical button on the plug.
    def set_childlock(self):
        new_state = not self.child_lock
        self.device.set_dps('40', new_state)
        self.child_lock = new_state
            
    
