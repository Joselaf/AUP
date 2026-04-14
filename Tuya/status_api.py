import json
import sys
import tinytuya
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_devices():
    """Load devices from devices.json"""
    with open("devices.json") as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get('devices', [])

def get_device_status(device):
    """Get status for a single device"""
    try:
        name = device.get("name", "Unknown")
        dev_id = device.get("id")
        ip = device.get("ip", "")
        key = device.get("key", "")
        category = device.get("category", "").lower()

        if not ip:
            return {
                "id": dev_id,
                "name": name,
                "status": "error",
                "error": "No IP address"
            }

        version = float(device.get("version", device.get("ver", "3.4")))

        d = tinytuya.OutletDevice(dev_id, ip, key)
        d.set_version(version)
        d.set_socketTimeout(2)  # Reduced timeout from 5 to 2 seconds
        result = d.status()
        dps = result.get("dps", {}) if result else {}

        return {
            "id": dev_id,
            "name": name,
            "category": category,
            "status": "online",
            "dps": dps
        }

    except Exception as e:
        return {
            "id": device.get("id"),
            "name": device.get("name", "Unknown"),
            "status": "error",
            "error": str(e)
        }

def get_all_statuses():
    """Get status for all devices concurrently"""
    devices = load_devices()
    statuses = []

    # Use ThreadPoolExecutor for concurrent device polling
    with ThreadPoolExecutor(max_workers=10) as executor:  # Limit to 10 concurrent connections
        future_to_device = {executor.submit(get_device_status, device): device for device in devices}

        for future in as_completed(future_to_device):
            status = future.result()
            statuses.append(status)

    return statuses

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "control":
        # Control device: python status_api.py control <device_id> <dps_key> <value>
        if len(sys.argv) < 5:
            print(json.dumps({"error": "Usage: python status_api.py control <device_id> <dps_key> <value>"}))
            sys.exit(1)

        device_id = sys.argv[2]
        dps_key = sys.argv[3]
        value = sys.argv[4]

        devices = load_devices()
        device = next((d for d in devices if d["id"] == device_id), None)

        if not device:
            print(json.dumps({"error": "Device not found"}))
            sys.exit(1)

        try:
            ip = device.get("ip", "")
            key = device.get("key", "")
            version = float(device.get("version", device.get("ver", "3.4")))

            d = tinytuya.OutletDevice(device_id, ip, key)
            d.set_version(version)
            d.set_socketTimeout(5)

            # Try to convert value to appropriate type
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
            elif "." in value and value.replace(".", "").isdigit():
                value = float(value)

            result = d.set_dps(dps_key, value)
            print(json.dumps({"success": True, "result": result}))
        except Exception as e:
            print(json.dumps({"error": str(e)}))

    else:
        # Get all statuses
        statuses = get_all_statuses()
        print(json.dumps(statuses))