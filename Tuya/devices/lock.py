import tinytuya

class lock:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.dps = self.device.status('dps',{})
        
        self.stats:{
            "id":self.id,
            "address:":self.ip, 
            "name":self.name,
            "finger_unlocked":self.dps.get('1'),##ID of th3e fingerprint used
            "password_unlocked":self.dps.get('2'),##ID of the local password used
            "password_generated":self.dps.get('3'),##Reports when an App-generated temporary code is used
            "card_unlocked":self.dps.get('5'),##Reports the ID of the RFID card/tag used
            "key":self.dps.get('7'),##Reports if a physical key was used (if supported)
            "door_status":self.dps.get('8'),##door open or close
            "alarms":self.dps.get('9'),##Reports errors (e.g., wrong_password, low_battery)
            "battery_level":self.dps.get('10'),##Remaining capacity in percentage (0–100%)
            "doorbell":self.dps.get('14'),##True when the doorbell button is pressed
            "remote":self.dps.get('61'),##True if door open remotelly
        }


        def get_status():
            return self.stats