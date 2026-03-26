import json
import tinytuya
from get_dps import get_alerts


def main():
    with open('devices.json') as f:
        devices = json.load(f)

    for device in devices:
        name = device.get('name', 'Unknown')
        if not device.get('ip'):
            continue

        print(f"{name} ({device.get('category', '?')}) — {device['ip']}")
        alerts = get_alerts(device)

        if alerts:
            for alert in alerts:
                print(f"  ⚠ {alert}")
        else:
            print(f"  ✓ OK")


if __name__ == "__main__":
    main()
