import json
import os
import csv
import io
from flask import Flask, jsonify, request, render_template, make_response

app = Flask(__name__)

DEVICES_FILE = os.path.join(os.path.dirname(__file__), "devices.json")

# --- Category mapping based on Tuya category codes and product names ---
CATEGORY_MAP = {
    "dlq": "breaker",          # circuit breakers
    "tdq": "heater",           # mini switches / heaters
    "ms":  "lock",             # smart locks (Fechaduras)
    "jtmspro": "smart_lock",   # smart locks (Smart Lock)
    "cz":  "smart_plug",       # smart plugs
    "kg":  "smart_plug",       # on/off switch
    "dj":  "bulb",             # lights / IR / ESMAX (category dj is overloaded)
    "hps": "presence_sensor",  # presence sensor
    "mcs": "contact_sensor",   # contact sensor
    "infrared_tv": "smart_tv", # TV sub-device
}

def load_devices():
    with open(DEVICES_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    devices = []
    for d in raw:
        cat_code = d.get("category", "")
        product_name = d.get("product_name", "")
        # Refine category for overloaded "dj" category
        dtype = CATEGORY_MAP.get(cat_code, "unknown")
        if dtype == "bulb":
            if "ESMAX" in product_name:
                dtype = "esmax"
            elif "IR" in product_name or "infrared" in cat_code.lower():
                dtype = "smart_ir"
        devices.append({
            "id": d.get("id"),
            "name": d.get("name"),
            "ip": d.get("ip", ""),
            "key": d.get("key"),
            "mac": d.get("mac", ""),
            "category": cat_code,
            "product_name": product_name,
            "icon": d.get("icon", ""),
            "type": dtype,
            "version": d.get("version", ""),
            "sub": d.get("sub", False),
            "parent": d.get("parent", None),
            "mapping": d.get("mapping", {}),  # Include DPS mapping
        })
    return devices

def dps_from_raw(raw_dps, mapping):
    """Convert numeric DPS keys to code names using the mapping."""
    result = {}
    # Tuya responses can return DPS keys as ints or strings depending on device/protocol.
    # Normalize both sides to strings so mapping is consistent.
    normalized_raw = {str(k): v for k, v in (raw_dps or {}).items()}
    normalized_mapping = {str(k): v for k, v in (mapping or {}).items()}

    # Create reverse mapping: numeric_key -> code_name
    for num_key, code_info in normalized_mapping.items():
        code_name = code_info.get("code", "")
        if code_name and num_key in normalized_raw:
            result[code_name] = normalized_raw[num_key]
    # Also include any numeric keys that aren't in mapping
    for num_key, value in normalized_raw.items():
        if num_key not in normalized_mapping:
            result[num_key] = value
    return result

def resolve_dps_key(command_dps, mapping):
    """
    Convert frontend DPS identifier to actual Tuya DPS key.
    Accepts:
      - numeric DPS keys (e.g. 1, "1")
      - code names from mapping (e.g. "switch_1")
    Returns a string/int key suitable for tinytuya.set_value().
    """
    if command_dps is None:
        return None

    # Pass through numeric DPS directly
    if isinstance(command_dps, int):
        return command_dps
    command_dps_str = str(command_dps)
    if command_dps_str.isdigit():
        return int(command_dps_str)

    # Resolve code name -> numeric DPS key using mapping
    normalized_mapping = {str(k): v for k, v in (mapping or {}).items()}
    for numeric_key, code_info in normalized_mapping.items():
        if str(code_info.get("code", "")) == command_dps_str:
            return int(numeric_key) if numeric_key.isdigit() else numeric_key

    # Fallback to original value if not found in mapping
    return command_dps

def normalize_command_value(value, dps_key, mapping):
    """Normalize command value to the expected DPS type when possible."""
    dps_key_str = str(dps_key)
    code_info = (mapping or {}).get(dps_key_str, {})
    expected_type = str(code_info.get("type", "")).lower()
    values_meta = code_info.get("values", {})

    if expected_type == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            v = value.strip().lower()
            if v in ("1", "true", "on", "yes", "enabled", "enable", "locked", "lock"):
                return True
            if v in ("0", "false", "off", "no", "disabled", "disable", "unlocked", "unlock"):
                return False
        return value

    if expected_type == "enum" and isinstance(value, str):
        # Common UI aliases for Tuya enum values
        aliases = {
            "memory": "last",
        }
        normalized = aliases.get(value.strip().lower(), value)
        valid_range = values_meta.get("range", [])
        if not valid_range or normalized in valid_range:
            return normalized
        return value

    return value

def mapping_has_code(mapping, code_name):
    """Return True if a mapping contains the given Tuya code name."""
    if not code_name:
        return False
    for code_info in (mapping or {}).values():
        if str(code_info.get("code", "")) == str(code_name):
            return True
    return False

def parse_tinytuya_error(result):
    """
    Return a normalized error message if a TinyTuya command response indicates failure.
    TinyTuya can return an error dict without raising an exception.
    """
    if not isinstance(result, dict):
        return None
    err = result.get("Error") or result.get("error")
    err_code = result.get("Err") or result.get("err")
    if err or err_code:
        if err and err_code:
            return f"{err} (code: {err_code})"
        return str(err or err_code)
    return None

COMMAND_EXCLUDED_PREFIXES = (
    "cur_",
    "add_",
    "battery_",
    "door_",
    "presence_",
    "distance",
    "tamper",
    "fault",
    "alarm_",
    "voltage_",
    "electric_",
    "power_",
    "temp_",
    "bright_",
    "illum",
    "odometer",
    "trip",
    "speed",
)

def parse_mapping_values(values):
    if isinstance(values, dict):
        return values
    if isinstance(values, str):
        try:
            parsed = json.loads(values)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {}
    return {}

def allowed_values_label(mapping_info):
    dps_type = str((mapping_info or {}).get("type", "")).lower()
    values = parse_mapping_values((mapping_info or {}).get("values", {}))

    if dps_type == "boolean":
        return "true | false"
    if dps_type == "enum":
        enum_range = values.get("range", [])
        return " | ".join(str(v) for v in enum_range) if enum_range else "enum"
    if dps_type == "integer":
        pieces = []
        for key in ("min", "max", "step", "unit"):
            value = values.get(key)
            if value is not None and value != "":
                pieces.append(f"{key} {value}")
        return ", ".join(pieces) if pieces else "integer"
    if dps_type == "string":
        maxlen = values.get("maxlen")
        return f"string (maxlen {maxlen})" if maxlen is not None else "string"
    return dps_type or "Any"

def build_supported_commands_matrix():
    matrix = []
    for device in load_devices():
        mapping = device.get("mapping", {})
        if not isinstance(mapping, dict):
            continue
        commands = []
        for dps_key, mapping_info in mapping.items():
            if not isinstance(mapping_info, dict):
                continue
            code = str(mapping_info.get("code", ""))
            if not code:
                continue
            lower_code = code.lower()
            if any(lower_code.startswith(prefix) for prefix in COMMAND_EXCLUDED_PREFIXES):
                continue
            commands.append({
                "code": code,
                "dps": str(dps_key),
                "allowed": allowed_values_label(mapping_info),
            })
        if not commands:
            continue
        commands.sort(key=lambda item: (item["code"], item["dps"]))
        matrix.append({
            "device_id": device.get("id"),
            "device_name": device.get("name"),
            "commands": commands,
        })
    return matrix

# ---- Routes ----

@app.route("/")
def index():
    response = make_response(render_template("index.html", ui_version="SIMPLE-UI-2026-04-14-B"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-UI-Version"] = "SIMPLE-UI-2026-04-14-B"
    return response

@app.route("/api/devices")
def api_devices():
    """Return all devices with their metadata (no live polling)."""
    devices = load_devices()
    return jsonify(devices)

@app.route("/api/commands-matrix")
def api_commands_matrix():
    return jsonify(build_supported_commands_matrix())

@app.route("/api/commands-matrix.csv")
def api_commands_matrix_csv():
    matrix = build_supported_commands_matrix()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["device_id", "device_name", "code", "dps", "allowed"])
    for entry in matrix:
        for cmd in entry["commands"]:
            writer.writerow([
                entry.get("device_id", ""),
                entry.get("device_name", ""),
                cmd.get("code", ""),
                cmd.get("dps", ""),
                cmd.get("allowed", ""),
            ])
    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = "attachment; filename=supported_commands_matrix.csv"
    return response

@app.route("/api/device/<device_id>/status")
def api_device_status(device_id):
    """
    Attempt live status poll for a specific device using local polling only.
    """
    devices = load_devices()
    device = next((d for d in devices if d["id"] == device_id), None)
    if not device:
        return jsonify({"error": "Device not found"}), 404

    ip = device.get("ip", "")
    key = device.get("key", "")
    dtype = device.get("type", "unknown")

    if not ip:
        return jsonify({"error": "No IP address. Device may be offline, undiscovered, or cloud-only. Run python -m tinytuya wizard again to refresh."}), 200

    try:
        import tinytuya
        dev = tinytuya.OutletDevice(device_id, ip, key)
        dev.set_version(float(device.get("version") or 3.3))
        raw = dev.status()
        raw_dps = raw.get("dps", {})
        
        # Convert numeric DPS keys to code names using device mapping
        mapping = device.get("mapping", {})
        dps = dps_from_raw(raw_dps, mapping)
        mapping_hits = sum(
            1
            for key, code_info in (mapping or {}).items()
            if code_info.get("code") in dps and str(key) in {str(k) for k in (raw_dps or {}).keys()}
        )

        result = {
            "type": dtype,
            "polling_mode": "local",
            "debug": {
                "requested_device_id": device_id,
                "polled_device_id": device.get("id"),
                "polled_ip": ip,
                "is_sub_device": bool(device.get("sub", False)),
                "parent_id": device.get("parent"),
                "raw_dps_count": len(raw_dps or {}),
                "mapped_dps_count": mapping_hits,
            },
        }

        # Parse known DPS by device type
        if dtype in ("breaker", "consumption_breaker", "general_circuit_breaker"):
            result.update({
                "state": dps.get("switch"),
                "fault": dps.get("fault"),
                "relay_status": dps.get("relay_status"),
                "child_lock": dps.get("child_lock"),
                "add_ele": dps.get("add_ele"),
                "amps": round((dps.get("cur_current") or 0) / 1000.0, 3),
                "watts": round((dps.get("cur_power") or 0) / 10.0, 2),
                "volts": round((dps.get("cur_voltage") or 0) / 10.0, 1),
            })
        elif dtype == "heater":
            result.update({
                "state": dps.get("switch_1"),
                "countdown": dps.get("countdown_1"),
                "relay_status": dps.get("relay_status"),
                "child_lock": dps.get("child_lock"),
            })
        elif dtype in ("lock", "smart_lock"):
            result.update({
                "door_status": dps.get("door_status"),
                "battery": dps.get("battery_percentage") or dps.get("battery_value"),
                "alarms": dps.get("alarm_lock"),
            })
        elif dtype == "smart_plug":
            result.update({
                "state": dps.get("switch_1"),
                "countdown": dps.get("countdown_1"),
                "child_lock": dps.get("child_lock"),
            })
        elif dtype == "bulb":
            result.update({
                "state": dps.get("switch_led"),
                "mode": dps.get("work_mode"),
                "brightness": dps.get("bright_value"),
                "colour_temp": dps.get("temp_value"),
            })
        elif dtype == "presence_sensor":
            result.update({
                "presence": dps.get("presence_state"),
                "illuminance": dps.get("bright_value"),
                "distance": dps.get("distance"),
            })
        elif dtype == "contact_sensor":
            result.update({
                "door_open": dps.get("doorcontact_state"),
                "battery_pct": dps.get("battery_percentage"),
                "battery_state": dps.get("battery_state"),
                "tamper": dps.get("tamper_alarm"),
            })
        elif dtype == "esmax":
            result.update({
                "switch_lock": dps.get("switch_lock"),
                "gear": dps.get("gear"),
                "lights": dps.get("lights"),
                "speed": round((dps.get("speed") or 0) / 10.0, 1),
                "battery": dps.get("battery"),
                "odometer": round((dps.get("odometer") or 0) / 10.0, 1),
                "trip": round((dps.get("trip") or 0) / 10.0, 1),
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Local polling failed: {str(e)}"}), 200

@app.route("/api/device/<device_id>/command", methods=["POST"])
def api_device_command(device_id):
    """Send a DPS command to a device using local polling only."""
    devices = load_devices()
    device = next((d for d in devices if d["id"] == device_id), None)
    if not device:
        return jsonify({"error": "Device not found"}), 404

    ip = device.get("ip", "")
    key = device.get("key", "")
    if not ip:
        return jsonify({"error": "No IP address. Device may be offline, undiscovered, or cloud-only. Run python -m tinytuya wizard again to refresh."}), 400

    body = request.get_json(silent=True) or {}
    dps_code = body.get("dps")  # Can be code name (switch_1) or numeric key (1)
    value = body.get("value")
    if dps_code is None:
        return jsonify({"error": "Missing 'dps' in request body"}), 400

    mapping = device.get("mapping", {})
    dps_key = resolve_dps_key(dps_code, mapping)

    # If a non-numeric DPS code wasn't found in mapping, reject early with guidance.
    dps_code_str = str(dps_code)
    if (
        not dps_code_str.isdigit()
        and isinstance(dps_key, str)
        and dps_key == dps_code_str
        and not mapping_has_code(mapping, dps_code_str)
    ):
        supported_codes = sorted(
            {
                str(code_info.get("code"))
                for code_info in (mapping or {}).values()
                if code_info.get("code")
            }
        )
        return jsonify({
            "error": f"Unsupported DPS code for this device: '{dps_code_str}'",
            "debug": {
                "requested_dps": dps_code,
                "device_id": device_id,
                "ip": ip,
                "supported_codes": supported_codes,
            },
        }), 400

    normalized_value = normalize_command_value(value, dps_key, mapping)

    try:
        import tinytuya
        dev = tinytuya.OutletDevice(device_id, ip, key)
        dev.set_version(float(device.get("version") or 3.3))
        try:
            result = dev.set_value(dps_key, normalized_value)
            command_error = parse_tinytuya_error(result)
            # Some firmwares are more reliable with set_status for boolean DPS.
            if command_error and isinstance(normalized_value, bool):
                result = dev.set_status(normalized_value, switch=dps_key)
                command_error = parse_tinytuya_error(result)
            if command_error:
                return jsonify({
                    "error": f"Local command failed: {command_error}",
                    "result": result,
                    "debug": {
                        "requested_dps": dps_code,
                        "resolved_dps_key": dps_key,
                        "requested_value": value,
                        "normalized_value": normalized_value,
                        "device_id": device_id,
                        "ip": ip,
                    },
                }), 500
        except Exception:
            # Some firmwares are more reliable with set_status for boolean DPS.
            if isinstance(normalized_value, bool):
                result = dev.set_status(normalized_value, switch=dps_key)
                command_error = parse_tinytuya_error(result)
                if command_error:
                    return jsonify({
                        "error": f"Local command failed: {command_error}",
                        "result": result,
                        "debug": {
                            "requested_dps": dps_code,
                            "resolved_dps_key": dps_key,
                            "requested_value": value,
                            "normalized_value": normalized_value,
                            "device_id": device_id,
                            "ip": ip,
                        },
                    }), 500
            else:
                raise
        return jsonify({
            "ok": True,
            "result": str(result),
            "debug": {
                "requested_dps": dps_code,
                "resolved_dps_key": dps_key,
                "requested_value": value,
                "normalized_value": normalized_value,
                "device_id": device_id,
                "ip": ip,
            },
        })
    except Exception as e:
        return jsonify({
            "error": f"Local command failed: {str(e)}",
            "debug": {
                "requested_dps": dps_code,
                "resolved_dps_key": dps_key,
                "requested_value": value,
                "normalized_value": normalized_value,
                "device_id": device_id,
                "ip": ip,
            },
        }), 500


if __name__ == "__main__":
    # Disable auto-reloader to avoid intermittent restarts that can break fetches.
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
