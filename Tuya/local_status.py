"""
Fetch status of all devices in devices.json every 30 seconds
Uses get_dps.py to check device-specific alerts by category
"""

import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from get_dps import get_alerts

DEVICES_FILE = "devices.json"
POLL_INTERVAL = 0

def load_devices():
    """Load devices from devices.json"""
    with open(DEVICES_FILE) as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get('devices', [])

def check_device(device):
    """Check a single device and return its alerts"""
    name     = device.get('name', 'Unknown')
    category = device.get('category', 'unknown')
    alerts   = get_alerts(device)
    return (name, category, alerts)

if __name__ == "__main__":

    devices  = load_devices()
    valid    = [d for d in devices if d.get('ip')]
    skipped  = [d for d in devices if not d.get('ip')]


    cycle = 0
    try:
        while True:
      

            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(check_device, d) for d in valid]
                results = [f.result() for f in as_completed(futures)]

            # Sort by category then name
            results.sort(key=lambda x: (x[1], x[0]))

            for name, category ,alerts in results:
                for alert in alerts:
                    print(f"{name}:{alert}")
                

            
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n\nStopped.")
