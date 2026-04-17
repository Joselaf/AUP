import tinytuya

class lock:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.status = self.device.status()
        self.dps = self.status.get('dps', {})

        self.stats = {
            "finger_unlocked":    self.dps.get('1'),   ## ID of fingerprint used
            "password_unlocked":  self.dps.get('2'),   ## ID of local password used
            "password_generated": self.dps.get('3'),   ## App-generated temp code
            "card_unlocked":      self.dps.get('5'),   ## RFID card/tag ID
            "key":                self.dps.get('7'),   ## Physical key used
            "door_status":        self.dps.get('8'),   ## True=open, False=closed
            "alarms":             self.dps.get('9'),   ## wrong_password, low_battery, etc.
            "battery_level":      self.dps.get('10'),  ## 0-100%
            "doorbell":           self.dps.get('14'),  ## True when doorbell pressed
            "remote":             self.dps.get('61'),  ## True if opened remotely
        }
        
        def get_status(self):
            if(self.ip):
                return self.stats
            else:
                return None
