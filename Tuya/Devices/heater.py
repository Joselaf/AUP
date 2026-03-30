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
        
    def get_id():
        return self.id

    def get_name():
        return self.name

    def get_state():
        return self.state

    def Toogle():
        new_state = not self.state
        self.device.set_dps(new_state, '1')
        self.state = new_state

    def get_targ_temp():
        return self.targ_temp

    def get_mode():
        return self.mode

    def set_targ_temp(temp):
        self.device.set_dps(temp, '2')
        self.targ_temp = temp

    def set_mode(mode):        
        self.device.set_dps(mode, '4')
        self.mode = mode

    
    def get_curr_temp():        
        return self.curr_temp
        
    def get_child_lock():
        return self.child_lock

    def set_child_lock(lock):
        self.device.set_dps(lock, '40')
        self.child_lock = lock

        



    



