import tinytuya

class smart_plug:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(id, ip, local_key)
        self.dps = self.device.status('dps', {})
        self.dps = self.dps.get('dps', self.dps) if isinstance(self.dps, dict) else {}
        self.refresh_stats()

    def refresh_stats(self):
        self.state        = self.dps.get('1')
        self.countdown    = self.dps.get('9')
        self.relay_status = self.dps.get('38')
        self.child_lock   = self.dps.get('40')

    def get_status(self):
        return {
            "id":           self.id,
            "address":      self.ip,
            "name":         self.name,
            "state":        self.state,
            "countdown":    self.countdown,
            "relay_status": self.relay_status,
            "child_lock":   self.child_lock,
        }

    ## Turns the device ON if it is OFF and vice-versa
    def Toogle(self):
        new_state = not self.dps.get('1')
        self.device.set_dps('1', new_state)

    ## Countdown Timer: Remaining time in seconds before auto-off.
    def set_countdown(self, value):
        self.device.set_dps('9', value)
        self.countdown = value

    ## Power-on State: What the plug does after a power cut (on, off, or memory).
    def set_relay_status(self, value):
        self.device.set_dps('38', value)
        self.relay_status = value

    ## Child Lock: Disables the physical button on the plug.
    def set_child_lock(self, value):
        self.device.set_dps('40', value)
        self.child_lock = value
