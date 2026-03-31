class door_sensor:
     def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.refresh_stats(self)
 
    def refresh_stats(self):
        self.dps = self.device.status('dps',{})
        self.door_contacts = self.dps('1')
        self.battery_percentage = self.dps('2')
        self.battery_state = self.dps('3')
        self.tamper_alarm = self.dps('4')



        def get_door_status():            
            if self.dps('1') == True:
                return "Door is open"
            else:
                return "Door is closed"
        
        def get_battery_percentage():
            return self.dps('2')
 
        def  get_battery_state():
            return(self.dps('3'))
        
        def get_tamper_alarm():
           if (self.dps('4') == True:
            return "case is OFF"
           else:
            return "case is ON"


        
        
