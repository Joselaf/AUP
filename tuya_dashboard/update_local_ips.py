#!/usr/bin/env python3
import json
import tinytuya

# Scan for local devices
print("Scanning for local Tuya devices...")
devices_local = tinytuya.deviceScan()
print(f"Found {len(devices_local)} local devices")

# Load current devices.json
with open('devices.json', 'r', encoding='utf-8') as f:
    devices = json.load(f)

# Create mapping of device IDs to local IPs
local_ip_map = {}
for ip, device_info in devices_local.items():
    device_id = device_info.get('id')
    if device_id:
        local_ip_map[device_id] = ip
        print(f"Found local device: {device_id} at {ip}")

# Update devices.json with local IPs
updated_count = 0
for device in devices:
    device_id = device.get('id')
    if device_id in local_ip_map:
        old_ip = device.get('ip', '')
        device['ip'] = local_ip_map[device_id]
        print(f"Updated {device['name']}: {old_ip} -> {device['ip']}")
        updated_count += 1

# Save updated devices.json
with open('devices.json', 'w', encoding='utf-8') as f:
    json.dump(devices, f, indent=2, ensure_ascii=False)

print(f"Updated {updated_count} devices with local IP addresses!")