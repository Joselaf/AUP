import tinytuya

class smart_lock:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.dps = self.device.status('dps',{})
        self.refresh_stats()
        
        self.stats:{
            "id":self.id,
            "address:":self.ip, 
            "name":self.name,
            "finger_unlocked":self.dps.get('1'),##ID of th3e fingerprint used
            "password_unlocked":self.dps.get('2'),##ID of the local password used
            "password_generated":self.dps.get('3'),##Reports when an App-generated temporary code is used
            "app_unlocked":self.dps.get('4'),##Remote Unlock: Appears as a request or action for remote opening
            "battery_percentage": self.dps.gtet('21'),##Battery Status: 0%–100%
            "alarm_lock":self.dps.get('38'),##Security alerts (Tamper, Wrong Try, Door Ajar)
            "video_request":self.dps.get('45'),##Triggered when someone presses the Doorbell on the lock
            "face_recognition":self.dps.get('50'),##(Specific to HR models) Reports the ID for Face Unlock
            "door_state":self.dps.get('63'),##Reports if the door is currently Open or Closed
        }

        def get_status():
            return self.stats
    


   
        
    





