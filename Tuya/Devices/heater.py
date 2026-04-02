import tinytuya

class heater:
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
        self.state = self.dps('1')
        self.countdown = self.dps('9')  
        self.relay_status = self.dps('38')
        self.child_lock = self.dps('40')
        self.switch_type = self.dps('42')

    ##returns the device id
    def get_id(self):
        return self.id
        
    ##retunrs the device name 
    def get_name(self):
        return self.name

    ##returns the device ip
    def get_ip(self):
        return self.ip
    

    ##returns if the device is ON/OFF
    def get_state(self):
        return self.state
    
    ##Turns the device ON if it is OFF and vice-versa
    def toggle(self):
        new_state = not self.state
        self.device.set_dps(new_state, '1')
        self.state = new_state

    ##sets the countdown value (in minutes) to turn the device OFF
    def set_countdown(self, value):
        self.device.set_dps(value, '9')
        self.countdown = value

    ##returns the countdown value
    def get_countdown(self):
        return self.countdown

    ##Power-on State: 0 (Off), 1 (On), 2 (Last state).
    def set_relay_status(self, value):
        self.device.set_dps(value, '38')
        self.relay_status = value

    ##returns the relay status (if the device is actually ON/OFF)
    def get_relay_status(self):
        return self.relay_status
    

    ##Physical Lock: Disables manual buttons if present. 
    def set_child_lock(self, lock):
        self.device.set_dps(lock, '40')
        self.child_lock = lock

    ##returns the child lock status
    def get_child_lock(self):
        return self.child_lock

    ##Switch Type: 1 - momentary, 2 - toggle, 3 - state
    def set_switch_type(self, value):
        self.device.set_dps(value, '42')
        self.switch_type = value
    
    ##returns the switch type
    def get_switch_type(self):
        return self.switch_type


        



    



