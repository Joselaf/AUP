import tinytuya

BATTERY_KEYS = {"battery_percentage", "battery_state", "battery_value", "va_battery"}
BREAKER_KEYS = {"switch", "switch_1", "tripped", "leakage_current", "fault"}
FIRE_KEYS    = {"smoke_sensor_status", "fire_alarm", "alarm_smoke", "smoke_sensor_state"}
PANIC_KEYS   = {"sos", "sos_state", "panic", "alarm"}


def get_alerts(device):
    """Connect to a device locally and return a list of alert strings."""
    ip       = device.get('ip')
    dev_id   = device.get('id')
    key      = device.get('key')
    version  = float(device.get('version') or 3.3)
    category = device.get('category', '')

    d = tinytuya.OutletDevice(dev_id, ip, key)
    d.set_version(version)
    result = d.status()

    if 'Error' in result:
        return [f"Error: {result['Error']}"]

    dps = result.get('dps', {})
    alerts = []

    # Battery check
    for dp in BATTERY_KEYS:
        val = dps.get(dp)
        if isinstance(val, int) and val <= BATTERY_LOW_THRESHOLD:
            alerts.append(f"Low battery ({val}%)")
        elif isinstance(val, str) and val.lower() in ('low', 'dead'):
            alerts.append(f"Low/dead battery ({val})")

    # Circuit breaker tripped
    if category in BREAKER_KEYS:
        for dp in BREAKER_DPS:
            val = dps.get(dp)
            if val is False:
                alerts.append("Circuit breaker tripped")
            elif isinstance(val, str) and val.lower() in ('trip', 'fault', 'tripped'):
                alerts.append(f"Circuit breaker fault ({val})")

    # Fire / smoke alarm
    if category in FIRE_KEYS:
        for dp in ALARM_DPS:
            val = dps.get(dp)
            if val is True or val == 'alarm':
                alerts.append("Fire/smoke alarm active")

    # Panic button
    if category in PANIC_KEYS:
        for dp in ALARM_DPS:
            val = dps.get(dp)
            if val is True or val == 'alarm':
                alerts.append("Panic button active")

    return alerts
