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

    def refresh_stats():
        self.state = self.dps.get('1')
        self.fault = self.dps.get('9')

    def toggle():
       new_state = not self.state
       self.device.set_dps('1', new_state)
       self.state = new_state
       return(new_state)

    def get_status():
        if(self.state):
            return("ON")
        elif(not self.state and self.fault):
            return(f"OFF:{self.fault}")
        else:
            return("OFF") 

    def atm_values():
        volt = dps.get('3') / 10.0
        amp = dps.get('4') / 1000.0
        watt = dps.get('5') / 10.0
        ##update values to class
        self.volts += volt
        self.amps +=amp
        self.watts += watt
        return (volt, amp, watt)