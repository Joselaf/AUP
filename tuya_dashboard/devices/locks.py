import tinytuya

class lock:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.dps = self.device.status('dps',{})
        self.refresh_stats()

    ##refreshs the stats from the device
    def refresh_stats(self):
        self.finger_unlocked = self.dps('1')
        self.password_unlocked = self.dps('2')
        self.temp_unlocked = self.dps('3')
        self.card_unlockecked = self.dps('5')
        self.key = self.dps('7')
        self.door_status = self.dps('8')
        self.alarms = self.dps('9')
        self.battery_level = self.dps('10')
        self.doorbell = self.dps('14')
        self.remote = self.dps('61')

    ##returns the device id
    def get_id(self):
        return self.id

    ##returns the device name
    def get_name(self):
        return self.name

    ##returns the device ip
    def get_ip(self):
        return self.ip

    ##Reports the ID of the fingerprint used to unlock. 
    def get_finger_unlocked(self):
        return self.finger_unlocked

    ##Reports the ID of the local password used.
    def get_password_unlocked(self):
        return self.password_unlocked
    
    ##Reports when an App-generated temporary code is used.
    def get_temp_unlocked(self):
        return self.temp_unlocked
    
    ##Reports the ID of the RFID card/tag used.
    def get_card_unlocked(self):
        return self.card_unlockeced
    

    ##Reports if a physical key was used (if supported).
    def get_key(self):
        return self.key

    ##True (Open) / False (Closed).
    def get_door_status(self):
        return self.door_status


    ##Reports errors (e.g., wrong_password, low_battery).
    def get_alarms(self):
        return self.alarms
    

    ##Remaining capacity in percentage (0–100%).
    def get_battery_level(self):
        return self.battery_level
    

    ##True when the doorbell button is pressed.
    def get_doorbell(self):
        return self.doorbell
        
