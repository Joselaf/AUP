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
        self.dps = self.device.status('dps',{})
        self.refresh_stats(self)

    ##refreshs the stats from the device
    def refresh_stats():
        self.state = self.dps.get('1')
        self.fault = self.dps.get('26')
        self.relay_status = self.dps.get('38')
        self.amps += dps.get('18') / 1000.0
        self.watts += dps.get('19') / 10.0
        self.volts += dps.get('20') / 10.0

    ##returns the device name
    def get_name():
        return(self.name)

    ##returns the device id
    def  get_id():
        return(self.id)

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

    ##power_on / power_off / last
    def set_relay_status(value):
        self.device.set_dps('38', value)
        self.relay_status = value

    def get_relay_status():
        return(self.relay_status)

    ##returns the instant volts, amps, and watts and updates the self values of the device 
    def atm_values():
        amp = dps.get('18') / 1000.0
        watt = dps.get('19') / 10.0
        volt = dps.get('20') / 10.0
        return (volt, amp, watt)