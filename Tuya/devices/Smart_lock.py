import json
import os
import logging
import tinytuya

# Setup logging to catch errors instead of silent 'pass'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_CFG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tinytuya.json")

def _get_cloud():
    try:
        with open(_CFG_PATH) as f:
            cfg = json.load(f)
        return tinytuya.Cloud(
            apiRegion=cfg["apiRegion"],
            apiKey=cfg["apiKey"],
            apiSecret=cfg["apiSecret"],
            apiDeviceID=cfg["apiDeviceID"],
        )
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load Cloud config: {e}")
        return None

class Smart_lock: # Changed to PascalCase (Python standard)
    def __init__(self, d_id, d_local_key, d_name, d_version=3.3):
        self.id = d_id
        self.local_key = d_local_key
        self.name = d_name
        self.version = d_version
        self._cloud = _get_cloud()
        self._codes = {}
        self.is_online = False
        
        # Logic to prevent false low battery alerts
        self._low_bat_count = 0
        self._BATTERY_THRESHOLD = 3 # Must be 'low' 3 times to alert
        
        self.refresh()

    def refresh(self):
        if not self._cloud:
            return False
        try:
            result = self._cloud.getstatus(self.id)
            if result and result.get("success") and result.get("result"):
                # Convert list of dicts to a single dictionary
                self._codes = {item["code"]: item["value"] for item in result["result"]}
                self.is_online = True
                return True
        except Exception as e:
            logger.debug(f"Refresh failed for {self.name}: {e}")
        
        self.is_online = False
        return False

    @property
    def stats(self):
        """Returns a cleaned dictionary of device states."""
        return {
            "battery_state":      self._codes.get("battery_state", "unknown"),
            "door_open":          self._codes.get("open_inside", False),
            "alarm":              self._codes.get("alarm_lock"),
            "unlock_fingerprint": self._codes.get("unlock_fingerprint"),
            "unlock_password":    self._codes.get("unlock_password"),
            "unlock_card":        self._codes.get("unlock_card"),
            "unlock_temporary":   self._codes.get("unlock_temporary"),
            "hijack":             self._codes.get("hijack", False),
           "battery_percentage": self._codes.get("battery_percentage", self._codes.get("residual_electricity","unknown")),
        }

    def remote_unlock(self):
        if not self._cloud: return None
        try:
            # Typical Tuya command format
            return self._cloud.sendcommand(self.id, {"commands": [{"code": "unlock_app", "value": True}]})
        except Exception as e:
            logger.error(f"Unlock command failed: {e}")
            return None

    def get_tui_table(self, table,name):
        self.refresh()
        status = "🔴 [bold red]OFFLINE[/]"
        bat_raw = self.stats["battery_state"]
        battery = f"[bold white]{bat_raw}[/]"
        door_state = "[bold yellow]Opened[/]" if self.stats["door_open"] else "[bold blue]Closed[/]"
        table.add_columns("Device", "Status", "Door State", "Battery")
        table.add_row(name,status,door_state,battery)

    def get_alerts(self):
        """Calculates alerts with debouncing for sensitive sensors."""
        self.refresh()
        alerts = []
        current_stats = self.stats

        # --- Debounced Battery Logic ---
        _battery = current_stats.get("battery_state", "").lower()
        if _battery == "low":
            self._low_bat_count += 1
        else:
            self._low_bat_count = 0 # Reset if it reports 'high' or 'middle'

        battery_pct = self._codes.get("battery_percentage")
        if battery_pct is not None and isinstance(battery_pct, (int, float)):
            if self._low_bat_count >= self._BATTERY_THRESHOLD and battery_pct < 20 or battery_pct < 20:
                alerts.append("Low Battery (Confirmed)")

        # --- Immediate Alerts ---
        if current_stats.get("alarm")!='low_battery': # Avoid duplicate low battery alert
            alerts.append(f"Alarm is triggered! ({self._codes.get('alarm_lock')})")
        if current_stats.get("hijack"):
            alerts.append(f"Hijack mode is active! ({self._codes.get('hijack')})")
            
        return alerts