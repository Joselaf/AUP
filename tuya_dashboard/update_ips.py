#!/usr/bin/env python3
import json

# Load devices.json
with open('devices.json', 'r', encoding='utf-8') as f:
    devices = json.load(f)

# Load tuya-raw.json
with open('tuya-raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# Create a mapping of device IDs to IP addresses and versions from raw data
ip_mapping = {}
for device in raw_data.get('result', []):
    device_id = device.get('id')
    ip = device.get('ip', '')
    # Try to determine version - this is a heuristic
    version = device.get('version', '3.3')  # default
    ip_mapping[device_id] = {'ip': ip, 'version': version}

# Update devices.json with IP addresses
for device in devices:
    device_id = device.get('id')
    if device_id in ip_mapping:
        device['ip'] = ip_mapping[device_id]['ip']
        device['version'] = ip_mapping[device_id]['version']
        print(f"Updated {device['name']}: IP={device['ip']}, version={device['version']}")
    else:
        print(f"No IP found for {device['name']}")

# Save updated devices.json
with open('devices.json', 'w', encoding='utf-8') as f:
    json.dump(devices, f, indent=2, ensure_ascii=False)

print("devices.json updated with IP addresses!")