import tinytuya

class smart_tv:
     def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(id, ip, local_key)
        self.dps = self.device.status('dps',{})
        self.refresh_stats(self)

        ##refreshs the stats from the device
        def refresh_stats():
            self.power = self.dps.get('1')
            self.volume = self.dps.get('2')
            self.mute = self.dps.get('3')
            self.mode = self.dps.get('4')
            self.tv_pannel = self.dps.get('16')
            self.source = self.dps.get('101')

             ##returns the device name
            def get_name():
                return(self.name)

            ##returns the device id
            def  get_id():
                return(self.id)

            ##returns the device ip
            def get_ip():
                return(self.ip)

        ##Turns the device ON if it is OFF and vice-versa
        def Toogle():
            new_state = not self.power
            self.device.set_dps(new_state, '1')
            self.power = new_state
        
        ##Volume setting : Normal range 0–100
        def set_volune(value):
            self.device.dps_set(value, '2')

        ##Turns the mute ON if it is OFF and vice-versa
        def set_mute():
            new_state = not self.mute
            self.device.set_dps(new_state, '1')
            self.mute = new_state
        

        ##mage patterns : such as standard, vivid, movie,user
        def set_mode(value):
            self.device.dps_set(value, '4')


        ##Control panel : Simulated remote control up/down/left/right/OK buttons
        def set_tv_pannel(value):
            self.device.dps_set(value, '16')
        

        ##Input source : such as HDMI1, HDMI2, AV, TV,USB
        def set_source(value):
            self.device.dps_set(value, '101')

        