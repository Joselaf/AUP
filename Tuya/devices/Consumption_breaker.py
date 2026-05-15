import tinytuya
from is_device_reachable import is_device_reachable
from breaker_code import breaker_code


class Consumption_breaker:
    def __init__(self, d_id, d_ip, d_local_key, d_name, d_version):
        self.id = d_id
        self.ip = d_ip
        self.local_key = d_local_key
        self.name = d_name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.device.set_version(d_version)
        self.dps = {}
        self.stats = {}
        self.refresh()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _normalize_state(self, raw_state):
        if isinstance(raw_state, bool):
            return raw_state
        if raw_state in (0, "0", False):
            return False
        if raw_state in (1, "1", True):
            return True
        for key in ("12", "16"):
            val = self.dps.get(key)
            if isinstance(val, bool):
                return val
            if val in (0, "0", False):
                return False
            if val in (1, "1", True):
                return True
        return raw_state not in (None, "None", "")

    def _parse_dps(self):
        try:
            watts = float(self.dps.get("19", 0)) / 10.0
        except (ValueError, TypeError):
            watts = 0.0
        try:
            amps = float(self.dps.get("18", 0)) / 1000.0
        except (ValueError, TypeError):
            amps = 0.0
        try:
            volts = float(self.dps.get("20", 0)) / 10.0
        except (ValueError, TypeError):
            volts = 0.0

        self.stats = {
            "state":        self._normalize_state(self.dps.get("1")),
            "amps":         amps,
            "watts":        watts,
            "volts":        volts,
            "fault":        self.dps.get("26"),
            "relay_status": self.dps.get("38"),
            "child_lock":   self.dps.get("40"),
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def refresh(self):
        status = self.device.status()
        self.dps = status.get("dps", {}) if status else {}
        self._parse_dps()

    def get_status(self):
        return self.stats if self.ip else None

    def get_ip(self):
        return self.ip

    def get_name(self):
        return self.name

    def get_tui_table(self, table, name):
        if is_device_reachable(self.ip):
            _status = "🟢 [bold green]ONLINE[/]"
            _state  = "[bold white]On[/]" if self.stats["state"] else "[bold white]OFF[/]"
            _fault  = "[bold white]None[/]" if self.stats["fault"] is None else f"[bold white]{breaker_code(self.stats['fault'])}[/]"
            _power = f"[bold yellow]{self.stats['watts']}W[/]"
        else:
            _status = "🔴 [bold red]OFFLINE[/]"
            _state = "[bold white]-[/]"
            _fault = "[bold white]-[/]"
            _power = "[bold white]-[/]"

        table.add_columns("Device", "Status", "State", "Fault","Power")
        table.add_row(name,_status,_state,_fault,_power)

    def get_alerts(self):
        alerts = []
        fault = self.stats.get("fault")
        state = self.stats.get("state")
        if state in (False, 0, "0"):
            if fault is not None:
                alerts.append(f"Breaker OFF:{breaker_code(fault)}")
                if self.stats["watts"] == 0 and self.stats["amps"] == 0:
                    alerts.append("BREAKER TRIPPED!")
            else:
                alerts.append("POWER OFF")
        return alerts

    def toggle(self):
        new_state = not self._normalize_state(self.dps.get("1"))
        self.device.set_dps("1", new_state)

    def set_relay_status(self, value):
        self.device.set_dps("38", value)

    def set_childlock(self):
        new_state = not self.stats.get("child_lock")
        self.device.set_dps("40", new_state)
