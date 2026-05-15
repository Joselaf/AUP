"""Shared base for cloud-connected lock devices (Lock, Smart_lock)."""
import json
import os
import logging
import tinytuya

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


class _CloudLockBase:
    def __init__(self, d_id, d_local_key, d_name, d_version=3.3):
        self.id = d_id
        self.local_key = d_local_key
        self.name = d_name
        self.version = d_version
        self._cloud = _get_cloud()
        self._codes: dict = {}
        self.is_online = False
        self.refresh()

    def refresh(self) -> bool:
        if not self._cloud:
            return False
        try:
            result = self._cloud.getstatus(self.id)
            if result and result.get("success") and result.get("result"):
                self._codes = {item["code"]: item["value"] for item in result["result"]}
                self.is_online = True
                return True
        except Exception as e:
            logger.debug(f"Refresh failed for {self.name}: {e}")
        self.is_online = False
        return False

    def remote_unlock(self):
        if not self._cloud:
            return None
        try:
            return self._cloud.sendcommand(
                self.id, {"commands": [{"code": "unlock_app", "value": True}]}
            )
        except Exception as e:
            logger.error(f"Unlock command failed: {e}")
            return None

    def get_tui_table(self, table, name):
        status      = "🟢 [bold green]ONLINE[/]" if self.is_online else "🔴 [bold red]OFFLINE[/]"
        battery     = f"[bold white]{self.stats['battery_state']}[/]"
        door_state  = "[bold yellow]Opened[/]" if self.stats["door_open"] else "[bold blue]Closed[/]"
        table.add_columns("Device", "Status", "Door State", "Battery")
        table.add_row(name, status, door_state, battery)
