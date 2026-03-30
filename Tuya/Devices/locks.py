import tinytuya

class lock:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.refresh_stats(self)
    
    def refresh_stats(self):
        self.dps = self.device.status('dps',{})
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

    def get_id():
        return self.id
    
    def get_name():
        return self.name

    def get_finger_unlocked():
        return self.finger_unlocked

    def get_password_unlocked():
        return self.password_unlocked
    
    
    def get_temp_unlocked():
        return self.temp_unlocked
    
    def get_card_unlocked():
        return self.card_unlockeced
    
    def get_key():
        return self.key

    def get_door_status():
        return self.door_status

    def get_alarms():
        return self.alarms
    
    def get_battery_level():
        return self.battery_level
    
    def get_doorbell():
        return self.doorbell
        
