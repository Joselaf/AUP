import tinytuya
from is_device_reachable import is_device_reachable
from breaker_code import breaker_code
from collections import deque
from datetime import datetime

_HISTORY_MAX = 2880


class General_circuit_breaker:
    def __init__(self, d_id, d_ip, d_local_key, d_name, d_version):
        self.id = d_id
        self.ip = d_ip
        self.local_key = d_local_key
        self.name = d_name
        self.device = tinytuya.OutletDevice(self.id, self.ip, self.local_key)
        self.device.set_version(d_version)
        self.dps = {}
        self.stats = {}

        # Energy accumulation
        self._cumulative_kwh: float = 0.0
        self._energy_history: deque = deque(maxlen=_HISTORY_MAX)

        self.refresh()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _accumulate_energy(self):
        """Accumulate add_ele (DP 17) into the running total."""
        try:
            raw = int(self.dps.get("17", 0))
        except (ValueError, TypeError):
            raw = 0
        if raw > 0:
            self._cumulative_kwh += raw / 1000.0
            self._energy_history.append((datetime.now(), self._cumulative_kwh))

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
            "state":          self.dps.get("1"),
            "amps":           amps,
            "watts":          watts,
            "volts":          volts,
            "cumulative_kwh": self._cumulative_kwh,
            "fault":          self.dps.get("26"),
            "relay_status":   self.dps.get("38"),
            "child_lock":     self.dps.get("40"),
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def refresh(self):
        status = self.device.status()
        self.dps = status.get("dps", {}) if status else {}
        self._accumulate_energy()
        self._parse_dps()

    def update_from_dps(self, dps: dict) -> None:
        """Called by UDPListener when a broadcast packet arrives."""
        self.dps.update(dps)
        self._accumulate_energy()
        self._parse_dps()

    def get_energy_history(self) -> list:
        """Return list of (datetime, cumulative_kwh) for graphing."""
        return list(self._energy_history)

    def get_status(self):
        return self.stats if self.ip else None

    def get_ip(self):
        return self.ip

    def get_name(self):
        return self.name

    def get_tui_table(self, table, name):
        if is_device_reachable(self.ip):
            status = "🟢 [bold green]ONLINE[/]"
            state  = "[bold white]On[/]" if self.stats["state"] else "[bold white]OFF[/]"
            fault  = "[bold white]None[/]" if self.stats["fault"] is None else f"[bold white]{breaker_code(self.stats['fault'])}[/]"
            power  = f"[bold yellow]{self.stats['watts']}W[/]"
            energy = f"[bold cyan]{self._cumulative_kwh:.3f}kWh[/]"
        else:
            status = "🔴 [bold red]OFFLINE[/]"
            state = fault = power = energy = "[bold white]-[/]"

        table.add_columns("Device", "Status", "State", "Fault", "Power", "Energy")
        table.add_row(name, status, state, fault, power, energy)

    def get_alerts(self):
        alerts = []
        fault = self.stats.get("fault")
        state = self.stats.get("state")
        if state is False:
            if fault is not None:
                alerts.append(f"Breaker OFF:{breaker_code(fault)}")
                if self.stats["watts"] == 0 and self.stats["amps"] == 0:
                    alerts.append("BREAKER TRIPPED!")
            else:
                alerts.append("POWER OFF")
        return alerts

    def toggle(self):
        new_state = not self.dps.get("1")
        self.device.set_status({"1": new_state})
