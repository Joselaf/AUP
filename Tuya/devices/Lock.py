from ._cloud_lock_base import _CloudLockBase


class Lock(_CloudLockBase):
    @property
    def stats(self):
        return {
            "battery_state":      self._codes.get("battery_state", "unknown"),
            "battery_percentage": self._codes.get("battery_percentage", self._codes.get("residual_electricity", "unknown")),
            "door_open":          self._codes.get("open_inside", False),
            "alarm":              self._codes.get("alarm_lock"),
            "unlock_fingerprint": self._codes.get("unlock_fingerprint"),
            "unlock_password":    self._codes.get("unlock_password"),
            "unlock_card":        self._codes.get("unlock_card"),
            "unlock_temporary":   self._codes.get("unlock_temporary"),
            "hijack":             self._codes.get("hijack", False),
        }

    def get_alerts(self):
        alerts = []
        battery_pct = self._codes.get("battery_percentage")
        if isinstance(battery_pct, (int, float)) and battery_pct < 20:
            alerts.append("Low Battery (Confirmed)")
        if self._codes.get("hijack"):
            alerts.append(f"Hijack mode is active! ({self._codes.get('hijack')})")
        return alerts
