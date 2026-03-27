import tinytuya

class Breaker:

    def init(device):
        self.device = device
        self.dps = device.status().get(("dps", {}) if result else {})

    def toggle():
        payload = {'1':True}
        self.device.set_dps(payload)

    def get_status():
       status = dps.get('1') 
       return(status)

    def get_current_amp():
        amps = dps.get('18', 0) / 1000.0
        return(amps)


    def get_current_wattage():
        watts = dps.get('19', 0) / 10.0
        return(watts)

    def get_current_voltge():
        volts = dps.get('20', 0) / 10.0
        return(volts)
