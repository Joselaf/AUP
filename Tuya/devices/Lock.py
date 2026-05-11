import json
import os
import tinytuya

_CFG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tinytuya.json")

def _get_cloud():
    with open(_CFG_PATH) as f:
        cfg = json.load(f)
    return tinytuya.Cloud(
        apiRegion=cfg["apiRegion"],
        apiKey=cfg["apiKey"],
        apiSecret=cfg["apiSecret"],
        apiDeviceID=cfg["apiDeviceID"],
    )

class Lock:
    def __init__(self, d_id, d_local_key, d_name, d_version=3.3):
        self.id = d_id
        self.local_key = d_local_key
        self.name = d_name
        self.version = d_version
        self._cloud = _get_cloud()
        self._codes = {}
        self.is_online = False
        self.refresh()

    def refresh(self):
        """Hybrid Refresh: Tries Cloud status, then sniffs for real-time local broadcasts."""
        # 1. Cloud Fallback
        try:
            result = self._cloud.getstatus(self.id)
            if result and result.get("success") and result.get("result"):
                self._codes = {item["code"]: item["value"] for item in result["result"]}
                self.is_online = True
        except Exception:
            self.is_online = False

        # 2. Local Real-Time Sniffing (UDP)
        try:
            # Scans for 1 second to see if the lock is currently awake on Wi-Fi
            devices = tinytuya.deviceScan(False, 1) 
            for addr in devices:
                if devices[addr]['id'] == self.id:
                    d = tinytuya.OutletDevice(self.id, addr, self.local_key)
                    d.set_version(self.version)
                    payload = d.status()
                    if payload and 'dps' in payload:
                        # Map numeric DPs to string codes for consistency
                        # DP 21: alarm_lock | DP 8: battery_percentage
                        rt = payload['dps']
                        if '21' in rt: self._codes['alarm_lock'] = rt['21']
                        if '8' in rt: self._codes['residual_electricity'] = rt['8']
                        self.is_online = True
        except Exception:
            pass
        return self.is_online

    @property
    def stats(self):
        """Consolidates cloud and local data into a clean dictionary."""
        return {
            "battery_state":      self._codes.get("battery_state", "unknown"),
            "percentage":         self._codes.get("residual_electricity") or self._codes.get("battery_percentage"),
            "door_open":          self._codes.get("open_inside", False),
            "alarm":              self._codes.get("alarm_lock"),
            "unlock_fingerprint": self._codes.get("unlock_fingerprint"),
            "unlock_password":    self._codes.get("unlock_password"),
            "unlock_card":        self._codes.get("unlock_card"),
            "unlock_temporary":   self._codes.get("unlock_temporary"),
            "hijack":             self._codes.get("hijack", False),
        }

    def get_alerts(self):
        self.refresh()
        _alerts = []
        s = self.stats
        
        # Match App Logic: Priority 1 (Alarm Event)
        if s["alarm"] == "low_battery":
            _alerts.append("Low Battery (App Alarm)")
        
        # Match App Logic: Priority 2 (Actual Percentage)
        if s["percentage"] is not None:
            try:
                if int(s["percentage"]) < 20:
                    _alerts.append(f"Low Battery: {s['percentage']}%")
            except (ValueError, TypeError):
                pass
        
        # Security Alarms
        if s["alarm"] and s["alarm"] != "low_battery" and s["alarm"] != "none":
            _alerts.append(f"Alarm: {str(s['alarm']).replace('_', ' ').title()}")
        
        if s["hijack"]:
            _alerts.append("Hijack Alert!")
            
        return _alerts

    def get_tui_table(self, table, name):
        """Displays status using the Rich library formatting."""
        if self.is_online:
            status = "🟢 [bold green]ONLINE[/]"
            s = self.stats
            
            # Show percentage if available, otherwise fallback to state
            bat_val = s["percentage"]
            if bat_val is not None:
                battery = f"[bold white]{bat_val}%[/]"
            else:
                battery = f"[bold white]{s['battery_state']}[/]"
                
            door_state = "[bold yellow]Opened[/]" if s["door_open"] else "[bold blue]Closed[/]"
        else:
            status = "🔴 [bold red]OFFLINE[/]"
            battery = "[bold white]-[/]"
            door_state = "[bold white]-[/]"

        # add_columns should ideally be handled by the parent table object
        # but kept here for compatibility with your existing loop logic
        table.add_columns("Device", "Status", "Door State", "Battery")
        table.add_row(name,status,door_state,battery)

    def remote_unlock(self):
        try:
            return self._cloud.sendcommand(self.id, {"commands": [{"code": "unlock_app", "value": True}]})
        except Exception:
            return None

    def get_name(self):
        return self.name