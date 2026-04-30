import json
import os
import tinytuya

_CFG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tinytuya.json')

def _get_cloud():
    with open(_CFG_PATH) as f:
        cfg = json.load(f)
    return tinytuya.Cloud(
        apiRegion=cfg['apiRegion'],
        apiKey=cfg['apiKey'],
        apiSecret=cfg['apiSecret'],
        apiDeviceID=cfg['apiDeviceID'],
    )

class smart_lock:
    def __init__(self, d_id, d_ip, d_local_key, d_name, d_version=3.3):
        self.id = d_id
        self.ip = d_ip
        self.local_key = d_local_key
        self.name = d_name
        self.version = d_version
        self._cloud = _get_cloud()
        self._codes = {}
        self.is_online = False
        self.refresh()

    def refresh(self):
        try:
            result = self._cloud.getstatus(self.id)
            if result and result.get('success') and result.get('result'):
                self._codes = {item['code']: item['value'] for item in result['result']}
                self.is_online = True
                return True
        except Exception:
            pass
        self.is_online = False
        return False

    @property
    def stats(self):
        return {
            "battery_state":      self._codes.get('battery_state', 'unknown'),
            "door_open":          self._codes.get('open_inside', False),
            "alarm":              self._codes.get('alarm_lock'),
            "doorbell":           self._codes.get('doorbell', False),
            "unlock_fingerprint": self._codes.get('unlock_fingerprint'),
            "unlock_password":    self._codes.get('unlock_password'),
            "unlock_card":        self._codes.get('unlock_card'),
            "hijack":             self._codes.get('hijack', False),
        }

    def remote_unlock(self):
        try:
            return self._cloud.sendcommand(self.id, {'commands': [{'code': 'unlock_app', 'value': 1}]})
        except Exception:
            return None

    def get_status(self):
        return self.stats if self.is_online else None

    def get_name(self):
        return self.name

    def get_tui_table(self, table, name):
        if self.is_online:
            status = "🟢 [bold green]ONLINE[/]"
            bat = self.stats['battery_state']
            battery = f"[bold white]{bat}[/]"
            door_state = "[bold yellow]Opened[/]" if self.stats['door_open'] else "[bold blue]Closed[/]"
        else:
            status = "🔴 [bold red]OFFLINE[/]"
            battery = "[bold white]-[/]"
            door_state = "[bold white]-[/]"
        table.add_columns("Device", "Status", "Door","Battery")
        table.add_row(name, status, door_state, battery)
