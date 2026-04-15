import threading

import tinytuya

class Breaker:
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
        self.refresh_stats()

    ##refreshs the stats from the device
    def refresh_stats(self):
        self.fault = self.dps.get('26')
        self.relay_status = self.dps.get('38')
        self.child_lock = self.dps.get('40')
        self.add_ele += self.dps.get('17')
        self.amps += self.dps.get('18') / 1000.0
        self.watts += self.dps.get('19') / 10.0
        self.volts += self.dps.get('20') / 10.0

    ##returns the device name
    def get_name(self):
        return(self.name)

    ##returns the device id
    def get_id(self):
        return(self.id)

    ##returns the device ip
    def get_ip(self):
        return(self.ip)

    ##Turns the device ON if it is OFF and vice-versa
    def toggle(self):
       new_state = not self.dps.get('1')
       self.device.set_dps('1', new_state)

    ##returns the status of the breaker
    def get_status(self):
        state = self.dps.get('1')
        if(state):
            return("ON")
        elif(self.fault):
            return(f"{self.fault}")
        else:
            return("OFF")

    ##power_on / power_off / memory
    def set_relay_status(self, value):
        self.device.set_dps('38', value)
        self.relay_status = value

    ##returns the relay status
    def get_relay_status(self):
        return(self.relay_status)

    ##returns the instant volts, amps, and watts of the device 
    def atm_values(self):
        amp = self.dps.get('18') / 1000.0
        volt = self.dps.get('20') / 10.0
        watt = self.dps.get('19') / 10.0
        add_ele = self.dps.get('17')
        return (volt, amp, watt, add_ele)

    ##Child Lock: Disables the physical button on the plug.
    def set_childlock(self):
        self.device.set_dps('40', True)
        self.child_lock = True

    ##returns the child lock status
    def get_child_lock(self):
        return(self.child_lock)
    
    ##returns the total consumption in KWH    
    def get_kwh(self):
        return(self.add_ele / 1000.0)

    ##returns atm_voltage    
    def get_volts(self):
        return(self.volts)

    ##returns atm_amps
    def get_amps(self):
        return(self.amps)
    