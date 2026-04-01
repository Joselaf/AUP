import tinytuya

class heater:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.refresh_stats(self)

    def refresh_stats(self):
        self.dps = self.device.status('dps',{})
        self.state = self.dps('1')
        self.targ_temp = self.dps('2')
        self.curr_temp = self.dps('3')
        self.mode = self.dps('4')
        self.child_lock = self.dps('40')

    ##returns the device id
    def get_id():
        return self.id
        
    ##retunrs the device name 
    def get_name():
        return self.name

    ##returns the device ip
    def egt_ip():
        return self.ip
    

    ##returns if the device is ON/OFF
    def get_state():
        return self.state
    
    ##Turns the device ON if it is OFF and vice-versa
    def Toogle():
        new_state = not self.state
        self.device.set_dps(new_state, '1')
        self.state = new_state

    ##returns the target temperature set previously
    def get_targ_temp():
        return self.targ_temp

    ##Target Temperature: The heat you want to reach (e.g., 22 = 22°C).
    def set_targ_temp(temp):
        self.device.set_dps(temp, '2')
        self.targ_temp = temp

    #returns the mode of the heater
    def get_mode():
        return self.mode

    ##work Mode: Usually manual, eco, or auto.
    def set_mode(mode):        
        self.device.set_dps(mode, '4')
        self.mode = mode

    ##Current Temperature: Room reading from the sensor probe.
    def get_curr_temp():        
        return self.curr_temp

    ##Physical Lock: Disables manual buttons if present. 
    def set_child_lock(lock):
        self.device.set_dps(lock, '40')
        self.child_lock = lock

    ##returns the child lock status
    def get_child_lock():
        return self.child_lock


        



    



