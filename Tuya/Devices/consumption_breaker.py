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
        self.refresh_stats(self)

    ##refreshs the stats from the device
    def refresh_stats():
        self.state = self.dps.get('1')
        self.fault = self.dps.get('26')
        self.relay_status = self.dps.get('38')
        self.child_lock = self.dps.get('40')
        self.add_ele = self.dps.get('17')
        self.amps += dps.get('18') / 1000.0
        self.watts += dps.get('19') / 10.0
        self.volts += dps.get('20') / 10.0



     ##returns the device name
    def get_name():
        return(self.name)

    ##returns the device id
    def  get_id():
        return(self.id)

    ##returns the device ip
    def get_ip():
        return(self.ip)

    ##Turns the device ON if it is OFF and vice-versa
    def toggle():
       new_state = not self.state
       self.device.set_dps('1', new_state)
       self.state = new_state
       return(new_state)

    ##returns the status of the breaker
    def get_status():
        if(self.state):
            return("ON")
        elif(not self.state and self.fault):
            return(f"OFF:{self.fault}")
        else:
            return("OFF")

    ##power_on / power_off / memory
    def set_relay_status(value):
        self.device.set_dps('38', value)
        self.relay_status = value

    ##returns the relay status
    def get_relay_status():
        return(self.relay_status)

    ##returns the instant volts, amps, and watts and updates the self values of the device 
    def atm_values():
        amp = self.dps.get('18') / 1000.0
        watt = self.dps.get('19') / 10.0
        volt = self.dps.get('20') / 10.0
        add_ele = self.dps('17')
        return (volt, amp, watt, add_ele)

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
        
