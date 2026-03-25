import tinytuya
import subprocess
import json

subprocess.run("python -m tinytuya scan", shell=True)

try:
    with open('snapshot.json') as file:
        data = json.load(file)
        
        # snapshot.json contains a 'devices' list at the top level
        devices = data.get('devices', [])
        
        if not devices:
            print("No devices found in snapshot.json")
        else:
            for device in devices:
                print(f"Name: {device.get('name', 'Unknown')}")
                print(f"  ID: {device.get('id', 'N/A')}")
                print(f"  IP: {device.get('ip', 'N/A')}")
                print(f"  Key: {device.get('key', 'N/A')}")
                
                # Print DPS values if available
                dps = device.get('dps', {})
                if dps:
                    print(f"  DPS: {dps}")
                print()

except FileNotFoundError:
    print("No such file or directory: 'snapshot.json'")
except json.JSONDecodeError:
    print("Error reading snapshot.json - file may be corrupted")
