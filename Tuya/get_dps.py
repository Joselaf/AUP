import tinytuya

BATTERY_LOW_THRESHOLD  = 20
BATTERY_DEAD_THRESHOLD = 5

BATTERY_KEYS = {"battery_percentage", "battery_state", "4", "15", "residue", "9", "3"}
FIRE_KEYS    = {"1", "smoke_sensor_status", "fire_alarm", "alarm_smoke"}
PANIC_KEYS   = {"1", "13", "sos", "sos_state", "panic"}

NON_BATTERY_CATEGORIES = {'dlq', 'td', 'dj', 'tdq', 'cz','wnykq', 'mcs', 'kg', 'infrared_tv'}


def get_alerts(device):
    name     = device.get("name", "Unknown")
    dev_id   = device.get("id")
    category = device.get("category", "").lower()
    ip       = device.get("ip", "")
    key      = device.get("key", "")

    try:
        version = float(device.get("version", device.get("ver", "3.4")))
    except (ValueError, TypeError):
        version = 3.4

    alerts = []

    # --- Get DPS ---
    try:
        if not ip:
            return ["No IP address - cannot connect locally"]
        d = tinytuya.OutletDevice(dev_id, ip, key)
        d.set_version(version)
        d.set_socketTimeout(5)
        result = d.status()
        dps = result.get("dps", {}) if result else {}
    except Exception as e:
        return [f"Connection error: {e}"]

    if not dps:
        return ["No DPS data received"]

    # --- Battery check (skip mains-powered devices) ---
    if category not in NON_BATTERY_CATEGORIES:
        for k in BATTERY_KEYS:
            val = dps.get(k)
            if val is None:
                continue
            if isinstance(val, (int, float)):
                if val <= BATTERY_DEAD_THRESHOLD:
                    alerts.append(f"⛔ Dead battery ({val}%)")
                elif val <= BATTERY_LOW_THRESHOLD:
                    alerts.append(f"⚠️ Low battery ({val}%)")
            elif isinstance(val, str):
                v = val.lower()
                if v in ("dead", "exhausted", "empty"):
                    alerts.append(f"⛔ Dead battery ('{val}')")
                elif v in ("low", "critical"):
                    alerts.append(f"⚠️ Low battery ('{val}')")

    # --- Circuit Breaker (dlq) ---
    if category == "dlq":
        switch = dps.get('1')
        fault  = dps.get('9', 0)
        if switch is False:
            alerts.append("⚡ Breaker OFF")
        if fault and fault != 0:
            alerts.append(f"⚠️ Breaker FAULT code: {fault}")

    # --- Heater (tdq) ---
    elif category == "tdq":
        switch = dps.get('1')
        fault  = dps.get('9', 0)
        if switch is False:
            alerts.append("⚡ Heater OFF")
        if fault and fault != 0:
            alerts.append(f"⚠️ Heater FAULT code: {fault}")

    # --- Magnetic Door Sensor (ms) ---
    elif category == "ms":
        if dps.get('2') is True:
            alerts.append(f"⚠️ TAMPER ALERT: {name} has been moved or opened!")
        # Door open/closed is status only — only alert if open
        if dps.get('1') is True:
            alerts.append(f"🔓 {name}: OPEN")

    # --- Fire / Smoke Alarm (ywbj) ---
    elif category == "ywbj":
        for k in FIRE_KEYS:
            val = dps.get(k)
            if val is None:
                continue
            if val is True or (isinstance(val, str) and val.lower() in ("alarm", "smoke", "fire", "detected")):
                alerts.append(f"🔥 FIRE/SMOKE ALARM ACTIVE ({k}: {val})")
            elif isinstance(val, int) and val == 1:
                alerts.append(f"🔥 FIRE/SMOKE ALARM ACTIVE ({k}: {val})")

    # --- Panic / SOS (sos) ---
    elif category == "sos":
        for k in PANIC_KEYS:
            val = dps.get(k)
            if val is None:
                continue
            if val is True or (isinstance(val, str) and val.lower() in ("sos", "panic", "alarm", "active")):
                alerts.append(f"🚨 PANIC/SOS ACTIVE ({k}: {val})")
            elif isinstance(val, int) and val == 1:
                alerts.append(f"🚨 PANIC/SOS ACTIVE ({k}: {val})")

    # --- Water Leak (jtmspro) ---
    elif category == "jtmspro":
        leak_state = dps.get('1')
        if leak_state in (True, 'alarm', 'water_leak'):
            alerts.append(f"🌊 CRITICAL: {name} DETECTED A WATER LEAK!")

    # --- Unknown ---
    else:
        alerts.append(f"ℹ️ Unknown category '{category}' - raw DPS: {dps}")

    return alerts