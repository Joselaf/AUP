import threading

import tinytuya

class breaker:
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
        self.dps= self.device.status().get('dps', {})
        
        ##It return the status of the device
        self.stats = {

            "state":self.dps.get('1'),
            "amps":(self.dps.get('18', 0) / 1000.0),
            "watts":(self.dps.get('19', 0) / 10.0),
            "volts":(self.dps.get('20', 0) / 10.0),
            "error":self.dps.get('26'),
            "relay_status":self.dps.get('38'),
            "child_lock":self.dps.get('40')
            }
        
    def get_status(self):
        if self.ip: 
            return self.stats
        else:
            return None
            


    ##Turns the device ON if it is OFF and vice-versa
    def toggle(self):
       new_state = not self.dps.get('1')
       self.device.set_dps('1', new_state)
       return new_state

    ##power_on / power_off / memory
    def set_relay_status(self, value):
        self.device.set_dps('38', value)
        self.relay_status = value
        return value

    ##Child Lock: Disables the physical button on the plug.
    def set_childlock(self):
        self.device.set_dps('40', True)
        self.child_lock = True


    