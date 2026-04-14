import tinytuya

class smart_plug:
        def __init__(self, id, ip, local_key, name):
            self.id = id
            self.ip = ip
            self.local_key = local_key
            self.name = name
            self.device = tinytuya.OutletDevice(id, ip, local_key)
            self.dps = self.device.status('dps',{})
            self.refresh_stats()

        ##refreshs the stats from the device
        def refresh_stats(self):
            self.state = self.dps('1')
            self.countdown = self.dps('9')
            self.relay_status = self.dps('38')
            self.child_lock = self.dps('40')

        ##returns the ID of the device
        def get_id(self):
            return self.id

        ##returns the name of the device
        def get_name(self):
            return self.name

        ##returns if the device is ON/OFF
        def get_state(self):
            return self.state

        ##Turns the device ON if it is OFF and vice-versa
        def Toogle(self):
            new_state = not self.state
            self.device.set_dps('1', new_state)
            self.state = new_state
            return(new_state)

        ##Countdown Timer: Remaining time in seconds before auto-off.
        def set_countdown(self, value):        
            self.device.set_dps('9', value)
            self.countdown = value

        ##returns the countdown set previously
        def get_countdown(self):        
            return self.countdown
        ##Power-on State: What the plug does after a power cut (on, off, or memory).
        def set_relay_status(self, value):
            self.device.set_dps('38', value)
            self.relay_status = value

        ##returns the relay status
        def get_relay_status(self):        
            return self.relay_status
        
        ##returns the child lock status
        def get_child_lock(self):
            return self.child_lock

        ##Child Lock: Disables the physical button on the plug.
        def set_child_lock(self, value):
            self.device.set_dps('40', value)
            self.child_lock = value




