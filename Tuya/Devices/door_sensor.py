class door_sensor:
        def __init__(self, id, ip, local_key, name):
            self.id = id
            self.ip = ip
            self.local_key = local_key
            self.name = name
            self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
            self.dps = self.device.status('dps',{})
            self.refresh_stats(self)


        ##refreshs the stats from the device    
        def refresh_stats(self):
            self.door_contacts = self.dps('1')
            self.battery_percentage = self.dps('2')
            self.battery_state = self.dps('3')
            self.tamper_alarm = self.dps('4')

        ##returns device name
        def get_name():
            return self.name
        
        ##returns the device id
        def get_id():
            return self.id
    
        ##returns if the door is open or close
        def get_door_status():            
            if (self.dps('1') == (True)):
                return "Door is open"
            else:
                return "Door is closed"
        
        ##returns the battery percentage
        def get_battery_percentage():
            return self.dps('2')
    
        ##returns Battery Status: low, middle, or high.
        def  get_battery_state():
            return(self.dps('3'))
        

        ##returns Tamper Alarm: True = case is opened/removed, False = case is closed
        def get_tamper_alarm():
           if (self.dps('4') == (True)):
            return "case is opened/removed"
           else:
            return "case is closed"


        
        
