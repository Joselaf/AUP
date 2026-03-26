import json
import tinytuya


# Open devices.json
with open('devices.json') as file:
    devices = json.load(file)


def get_status(id, name, ip, key, version):
    device = tinytuya.OutletDevice(id, ip, key)
    device.set_version(version)
    status = device.status()
    dps = status.get('dps', {})
    watts = dps.get('19', 0) / 10
    print(watts)

# Loop through devices and get local status
for device in devices:
    device_NAME = device.get('name', 'none')
    device_ID = device.get('id')
    devce_IP = device.get('ip')
    device_KEY = device.get('key')
    device_VERSION = device.get('version')
    if devce_IP:
        print(f"{device_NAME} has an IP:{devce_IP}")
        get_status(device_ID, device_NAME, devce_IP, device_KEY, device_VERSION)
    else:
        continue

