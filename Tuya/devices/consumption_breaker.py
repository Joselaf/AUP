import tinytuya
from is_device_reachable import is_device_reachable

class consumption_breaker:
    def __init__(self, d_id, d_ip, d_local_key, d_name, d_version):
        self.id = d_id
        self.ip = d_ip
        self.local_key = d_local_key
        self.name = d_name
        self.device = tinytuya.OutletDevice(d_id, d_ip, d_local_key)
        self.device.set_version(d_version) 
        
        self.status = self.device.status()
        
        if self.status is not None:
            self.dps = self.status.get('dps', {})
        else:
            self.dps = {}

        # 1. PRE-CALCULATE values with safety checks
        try:
            self.watts = float(self.dps.get('19', 0)) / 10.0
        except (ValueError, TypeError):
            self.watts = 0.0

        try:
            self.amps = float(self.dps.get('18', 0)) / 1000.0
        except (ValueError, TypeError):
            self.amps = 0.0

        try:
            self.volts = float(self.dps.get('20', 0)) / 10.0
        except (ValueError, TypeError):
            self.volts = 0.0

        # 2. DEFINE the dictionary using the pre-calculated values
        self.stats = {
            "state": self.dps.get('1'),
            "amps": self.amps,
            "watts": self.watts,
            "volts": self.volts,
            "error": self.dps.get('26'),
            "relay_status": self.dps.get('38'),
            "child_lock": self.dps.get('40')
        }

    ##It return the status of the device
    def get_status(self):
        if(self.ip):
            return self.stats
        else:
            return None

    def get_tui_table(self,table,name):
        error = None
        state = None
        if is_device_reachable(self.ip):
            status = "🟢 [bold green]ONLINE[/]"
            state = f"[bold white]On[/]" if {self.stats['state']} else "[bold white]OFF[/]"
            error = f"[bold white]{self.stats['error']}[/]" if {self.stats['error']} else "[bold white]-[/]"
        else:
            status = "🔴 [bold red]OFFLINE[/]"
            state = "[bold white]-[/]"
            error = "[bold white]-[/]"
        
        table.add_columns("Device", "Status", "State", "Error")
        table.add_row(name, status, state, error)


    def get_ip(self):
        return self.ip
    
    def get_name(self):
        return self.name   
        
    
    ##Turns the device ON if it is OFF and vice-versa
    def toggle(self):
       new_state = not self.dps.get('1')
       self.device.set_dps('1', new_state)



    ##power_on / power_off / memory
    def set_relay_status(self, value):
        self.device.set_dps('38', value)
        self.relay_status = value



        ##Child Lock: Disables the physical button on the plug.
    def set_childlock(self):
        new_state = not self.child_lock
        self.device.set_dps('40', new_state)
        self.child_lock = new_state
            
    
