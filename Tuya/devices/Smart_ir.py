import tinytuya
from is_device_reachable import is_device_reachable

class Smart_ir:
    def __init__(self,d_id,d_ip,d_local_key,d_name,d_version):
        self.id = d_id
        self.ip = d_ip
        self.local_key = d_local_key
        self.name = d_name
        self.device = tinytuya.OutletDevice(self.id,self.ip,self.local_key)
        self.device.set_version(d_version)
        self.status = self.device.status()
        if self.status is not None:
             self.dps = self.status.get('dps', {})
        else:
            self.dps = {}
        self.stats = {
            "id":      self.id,
            "address": self.ip,
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
        status = "🟢 [bold green]ONLINE[/]" if is_device_reachable(self.ip) else "🔴 [bold red]OFFLINE[/]"
        table.add_columns("Device", "Status")
        table.add_row(name, status)
    
    def get_alerts(self):
       return []
    
    def refresh(self):
        self.status = self.device.status()
        if self.status is not None:
            self.dps = self.status.get('dps', {})
        else:
            self.dps = {}

    ## Send Code: The raw IR code (Base64) to be emitted.
    def send_ir_code(self, code):
        _payload = self.device.generate_payload(tinytuya.CONTROL, {'1': code})
        self.device.send(_payload)

    ## Learning Mode: Receives and reports the IR code from a physical remote.
    def enter_learning_mode(self):
        _payload = self.device.generate_payload(tinytuya.CONTROL, {'2': True})
        self.device.send(_payload)
