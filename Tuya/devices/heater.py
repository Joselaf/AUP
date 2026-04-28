import tinytuya
from is_device_reachable import is_device_reachable

class heater:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.status = self.device.status()
        self.dps = self.status.get('dps', {})
        
        self.stats = {
            "state":self.dps.get('1'),##The device is on or off
            "countdown":self.dps.get('9'),##countdown value (in minutes) to turn the device OFF
            "relay_status":self.dps.get('83'),##Power-on State: 0 (Off), 1 (On), 2 (Last state)
            "child_lock":self.dps.get('40'),##Physical Lock: Disables manual buttons if present
            "switch_type":self.dps.get('42') ##Switch Type: 1 - momentary, 2 - toggle, 3 - state
            
        }
        
    def get_status(self):
        if(self.ip):
            return self.stats
        else:
            return None
    
    def get_ip(self):
        return self.ip
    
    def get_name(self):
        return self.name
    
    def get_tui_table(self,table,name):
        status = None
        state = None
        if is_device_reachable(self.ip):
            status =  "🟢[bold green]ONLINE[/]"
            state = "[bold yellow]ON[/]" if self.stats['state'] else "[bold blue]OFF[/]"
        else:
            status = "🔴[bold red]OFFLINE[/]"
            state = "[bold white]-[/]"
          
        table.add_columns("Device", "Status", "Power")
        table.add_row(name, status, details)

    ##Turns the device ON if it is OFF and vice-versa
    def toggle(self):
        new_state = not self.dps.get('1')
        self.device.set_dps('1', new_state)

    ##sets the countdown value (in minutes) to turn the device OFF
    def set_countdown(self, value):
        self.device.set_dps(value, '9')
        self.countdown = value

    ##Power-on State: 0 (Off), 1 (On), 2 (Last state).
    def set_relay_status(self, value):
        self.device.set_dps(value, '38')
        self.relay_status = value

    

    ##Physical Lock: Disables manual buttons if present. 
    def set_child_lock(self, lock):
        self.device.set_dps(lock, '40')
        self.child_lock = lock


    ##Switch Type: 1 - momentary, 2 - toggle, 3 - state
    def set_switch_type(self, value):
        self.device.set_dps(value, '42')
        self.switch_type = value
    

        



    



