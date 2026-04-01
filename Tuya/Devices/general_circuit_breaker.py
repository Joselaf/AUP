import tinytuya

class general_circuit_breaker:

    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(id, ip, local_key)
        self.add_ele = 0.0
        self.dps = self.device.status('dps',{})
        self.refresh_stats(self)
        
        ##returns the device id
        def get_id():
            return(self.id)

        ##returns the device name 
        def get_name():
            return(self.name)
        
        ##returns the device ip
        def get_ip():
            return(self.ip)


        ##refreshs the stats from the device
        def refresh_stats():
            self.switch = self.dps.get('1')
            self.add_ele += self.dps.get('17')
            self.relay_status = self.dps.get('38')
            self.child_lock = self.dps.get('40')

        ##Turns the device ON if it is OFF and vice-versa
        def toogle():
            new_state = not self.state
            self.device.set_dps('1', new_state)
            self.state = new_state

        ##power_on / power_off / memory
        def set_relay_status(value):
            self.device.set_dps('38', value)
            self.relay_status = value


        ##returns the relay status
        def get_relay_status():
            return(self.relay_status)

        ##Child Lock: Disables the physical button on the plug.
        def set_childlock():
            self.device.set_dps('40', True)
            self.child_lock = True

        ##returns the child lock status
        def get_child_lock():
            return(self.child_lock)
        
        ##returns the total consumption in KWH    
        def get_kwh():
            return(self.add_ele / 1000.0)

        ##returns atm_voltage    
        def get_volts():
            return(self.volts)

        ##returns atm_amps
        def get_amps():
            return(self.amps)
        
    