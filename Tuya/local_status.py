"""
Fetch status of all devices in snapshot.json every 30 seconds
"""

import tinytuya
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

DEVICES_FILE = "devices.json"
POLL_INTERVAL = 30

def load_devices():
    """Load devices from devices.json"""
    with open(DEVICES_FILE) as f:
        data = json.load(f)
    # devices.json is a plain list, snapshot.json wraps in {'devices': [...]}
    return data if isinstance(data, list) else data.get('devices', [])

def get_device_status(device):
    """Fetch status from a single device locally"""
    name = device.get('name', 'Unknown')
    dev_id = device.get('id')
    ip = device.get('ip', '')
    key = device.get('key', '')
    ver = float(device.get('version', device.get('ver', '3.4')))

    if not ip:
        return (name, None, "No IP address")

    try:
        d = tinytuya.OutletDevice(dev_id=dev_id, address=ip, local_key=key, version=ver)
        d.set_socketTimeout(5)
        status = d.status()

        if status and 'dps' in status:
            return (name, status['dps'], None)
        else:
            return (name, None, "No DPS data")
    except Exception as e:
        return (name, None, str(e))

def print_status(results):
    """Print device statuses"""
    print(f"\n{'='*60}")
    print(f"Device Status - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")

    for name, dps, error in sorted(results, key=lambda x: x[0]):
        if dps:
            print(f"\n✓ {name}")
            for key, value in dps.items():
                print(f"    DPS {key}: {value}")
        else:
            print(f"\n✗ {name}: {error}")

if __name__ == "__main__":
    print("=" * 60)
    print("LOCAL DEVICE STATUS MONITOR")
    print(f"Polling every {POLL_INTERVAL} seconds")
    print("=" * 60)

    devices = load_devices()
    # Filter out devices with no IP
    valid = [d for d in devices if d.get('ip')]
    skipped = [d for d in devices if not d.get('ip')]

    print(f"\nLoaded {len(devices)} device(s)")
    print(f"  ✓ {len(valid)} with IP (will be polled)")
    print(f"  ✗ {len(skipped)} without IP (skipped): {[d.get('name') for d in skipped]}")
    print("\nPress Ctrl+C to stop\n")

    cycle = 0
    try:
        while True:
            cycle += 1
            start = time.time()

            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(get_device_status, d) for d in valid]
                results = [f.result() for f in as_completed(futures)]

            print_status(results)

            elapsed = time.time() - start
            print(f"\n  Cycle {cycle} completed in {elapsed:.2f}s")

            sleep_time = max(0, POLL_INTERVAL - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n\nStopped.")
