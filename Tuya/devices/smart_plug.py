import tinytuya
from is_device_reachable import is_device_reachable
class smart_plug:
    def __init__(self, id, ip, local_key, name):
        self.id = id
        self.ip = ip
        self.local_key = local_key
        self.name = name
        self.device = tinytuya.OutletDevice(id, ip, local_key)
        self.status = self.device.status()
        self.dps = self.status.get('dps', {})
        
        self.stats = {
            "state":        self.dps.get('1'),
            "countdown":    self.dps.get('9'),
            "relay_status": self.dps.get('38'),
            "child_lock":   self.dps.get('40'),
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

    def gte_tui_table(self,table,nme):
        status = None
        state = None
        if is_device_reachable(self.ip):
            status = "🟢[bold green]ONLINE[/]"
            state = "[bold white]ON[/]" if self.stats['state'] else "[bold white]OFF[/]"
        else:
            status = "🔴[bold red]OFFLINE[/]"
            state = "[bold white]-[/]"
        table.add_columns("Device", "Status", "State")
        table.add_row(name, status, state)
        return table
            
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
