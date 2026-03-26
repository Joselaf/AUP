import tinytuya

BATTERY_LOW_THRESHOLD  = 20
BATTERY_DEAD_THRESHOLD = 5

# DPS keys to check per alert type
BATTERY_KEYS = {"battery_percentage", "battery_state", "battery_value", "va_battery"}
BREAKER_KEYS = {"switch", "switch_1", "tripped", "leakage_current", "fault"}
FIRE_KEYS    = {"smoke_sensor_status", "fire_alarm", "alarm_smoke", "smoke_sensor_state"}
PANIC_KEYS   = {"sos", "sos_state", "panic", "alarm"}


def get_alerts(device):
    """Connect to a device locally and return a list of alert strings."""
    ip      = device.get("ip")
    dev_id  = device.get("id")
    key     = device.get("key")
    version = float(device.get("version") or device.get("ver") or 3.3)

    d = tinytuya.OutletDevice(dev_id, ip, key)
    d.set_version(version)
    d.set_socketTimeout(5)
    result = d.status()

    if not result or "Error" in result:
        return [f"Error: {result.get('Error', 'No response')}"]

    dps    = result.get("dps", {})
    alerts = []

    # --- Battery (runs on all devices; skipped automatically if no battery DPS present) ---
    for key in BATTERY_KEYS:
        val = dps.get(key)
        if val is None:
            continue
        if isinstance(val, (int, float)):
            if val <= BATTERY_DEAD_THRESHOLD:
                alerts.append(f"Dead battery ({val}%)")
            elif val <= BATTERY_LOW_THRESHOLD:
                alerts.append(f"Low battery ({val}%)")
        elif isinstance(val, str):
            v = val.lower()
            if v in ("dead", "exhausted", "empty"):
                alerts.append(f"Dead battery ('{val}')")
            elif v in ("low", "critical"):
                alerts.append(f"Low battery ('{val}')")

    # --- Circuit breaker (checks DPS keys directly, no category needed) ---
    for key in BREAKER_KEYS:
        val = dps.get(key)
        if val is None:
            continue
        if key in ("switch", "switch_1") and val is False:
            alerts.append(f"Circuit breaker tripped ({key} is OFF)")
        elif key == "tripped" and val is True:
            alerts.append("Circuit breaker tripped")
        elif key == "fault" and val:
            alerts.append(f"Circuit breaker fault ({val})")
        elif key == "leakage_current" and isinstance(val, (int, float)) and val > 0:
            alerts.append(f"Leakage current detected ({val} mA)")

    # --- Fire / smoke alarm ---
    for key in FIRE_KEYS:
        val = dps.get(key)
        if val is None:
            continue
        if val is True or (isinstance(val, str) and val.lower() in ("alarm", "smoke", "fire", "detected")):
            alerts.append(f"Fire/smoke alarm active ({key}: {val})")
        elif isinstance(val, int) and val == 1:
            alerts.append(f"Fire/smoke alarm active ({key}: {val})")

    # --- Panic / SOS button ---
    for key in PANIC_KEYS:
        val = dps.get(key)
        if val is None:
            continue
        if val is True or (isinstance(val, str) and val.lower() in ("sos", "panic", "alarm", "active")):
            alerts.append(f"Panic/SOS active ({key}: {val})")
        elif isinstance(val, int) and val == 1:
            alerts.append(f"Panic/SOS active ({key}: {val})")

    return alerts