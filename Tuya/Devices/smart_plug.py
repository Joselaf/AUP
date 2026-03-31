import tinytuya

class smart_plug:
        def __init__(self, id, ip, local_key, name):
            self.id = id
            self.ip = ip
            self.local_key = local_key
            self.name = name
            self.device = tinytuya.OutletDevice(id, ip, local_key)
            self.dps = self.device.status('dps',{})
            self.refresh_stats(self)


        def refresh_stats(self):
            self.state = self.dps('1')
            self.countdown = self.dps('9')
            self.relay_status = self.dps('38')
            self.child_lock = self.dps('40')


        def get_id():
            return self.id

        def get_name():
            return self.name
        
        def get_state():
            return self.state

        def Toogle():
            new_state = not self.state
            self.device.set_dps('1', new_state)
            self.state = new_state
            return(new_state)
        
        def set_countdown(value):        
            self.device.set_dps('9', value)
            self.countdown = value

        def get_countdown():        
            return self.countdown
        
        def set_relay_status(value):
            self.device.set_dps('38', value)
            self.relay_status = value

        def get_relay_status():        
            return self.relay_status
        
        def get_child_lock():
            return self.child_lock
        
        def set_child_lock(value):
            self.device.set_dps('40', value)
            self.child_lock = value




