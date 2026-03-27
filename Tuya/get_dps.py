import tinytuya

BATTERY_LOW_THRESHOLD  = 20
BATTERY_DEAD_THRESHOLD = 5

# --- Category Mapping ---
# dlq  = Circuit Breaker
# ywbj = Smoke / Fire Alarm
# sos  = Panic / SOS Button

BATTERY_KEYS = {"battery_percentage", "battery_state", "4", "15", "residue"}
BREAKER_KEYS = {"1","9", "fault", "tripped", "leakage_current", "switch", "switch_1"}
FIRE_KEYS    = {"1", "smoke_sensor_status", "fire_alarm", "alarm_smoke"}
PANIC_KEYS   = {"1", "13", "sos", "sos_state", "panic"}


def get_alerts(device):
    """Connect to a device via cloud and return a list of alert strings."""
    name     = device.get("name", "Unknown")
    dev_id   = device.get("id")
    category = device.get("category", "").lower()
    ip       = device.get("ip", "")
    key      = device.get("key", "")
    version  = float(device.get("version", device.get("ver", "3.4")))

    alerts = []

    # --- Get DPS ---
    try:
        if ip:
            # Local connection
            d = tinytuya.OutletDevice(dev_id, ip, key)
            d.set_version(version)
            d.set_socketTimeout(5)
            result = d.status()
            dps = result.get("dps", {}) if result else {}
        else:
            return [f"No IP address - cannot connect locally"]
    except Exception as e:
        return [f"Connection error: {e}"]

    if not dps:
        return [f"No DPS data received"]

    # --- Battery check (all devices) ---
    for k in BATTERY_KEYS:
        val = dps.get(k)
        if val is None:
            continue
        if isinstance(val, (int, float)):
            if val <= BATTERY_DEAD_THRESHOLD:
                alerts.append(f"⛔ Dead battery ({val}%)")
            elif val <= BATTERY_LOW_THRESHOLD:
                alerts.append(f"⚠️  Low battery ({val}%)")
        elif isinstance(val, str):
            v = val.lower()
            if v in ("dead", "exhausted", "empty"):
                alerts.append(f"⛔ Dead battery ('{val}')")
            elif v in ("low", "critical"):
                alerts.append(f"⚠️  Low battery ('{val}')")

    # --- Circuit Breaker (dlq) ---
    if category == "dlq":
        # DPS '1'  = switch state (True=ON, False=OFF/tripped)
        # DPS '9'  = fault code (0=OK)
        # DPS '17' = total energy (kWh * 100)
        # DPS '18' = current (mA)
        # DPS '19' = power (W * 10)
        # DPS '20' = voltage (V * 10)

        switch = dps.get('1')
        fault  = dps.get('9', 0)

        if switch is False:
            alerts.append(f"⚡ Breaker OFF")
        elif switch is True:
            alerts.append(f"✅ Breaker ON")

        if fault and fault != 0:
            alerts.append(f"⚠️  Breaker FAULT code: {fault}")


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
        
        if not alerts:
            alerts.append("✅ No smoke/FIRE detected")

    # --- Panic / SOS Button (sos) ---
    elif category == "sos":
        for k in PANIC_KEYS:
            val = dps.get(k)
            if val is None:
                continue
            if val is True or (isinstance(val, str) and val.lower() in ("sos", "panic", "alarm", "active")):
                alerts.append(f"🚨 PANIC/SOS ACTIVE ({k}: {val})")
            elif isinstance(val, int) and val == 1:
                alerts.append(f"🚨 PANIC/SOS ACTIVE ({k}: {val})")
        
        if not alerts:
            alerts.append("✅ No panic/SOS active")

    # --- Unknown category ---
    else:
        alerts.append(f"ℹ️  Unknown category '{category}' - raw DPS: {dps}")

    return alerts


