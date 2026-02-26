from tuya_connector import TuyaOpenAPI
import time
import threading
## credentials from the cloud project you can find these in the Tuya IoT Platform
ACCESS_ID = "c8uhx3vs89grhea8mg7p"
ACCESS_KEY = "7221603a3b754d8b89b30c8dc9114b0d"
##It is used to connect to the API
api = TuyaOpenAPI("https://openapi.tuyaeu.com", ACCESS_ID, ACCESS_KEY)
api.connect()
## It fetches all the devices of the user and returns a list of devices.
def get_devices():
    devices, seen = [], set()
    for _ in range(10):
        body = {"page_size": 20}
        if devices:
            body["last_id"] = devices[-1]['id']
        
        result = api.get("/v2.0/cloud/thing/device", body).get("result", [])
        if not result:
            break
        
        for d in result:
            if d['id'] not in seen:
                seen.add(d['id'])
                devices.append(d)
        
        if len(result) < 20:
            break
    return devices

##gets the info of the device
def get_info(device_id):
    return api.get(f"/v1.0/devices/{device_id}")["result"]
## gets the status of the device
def get_status(device_id):
    return api.get(f"/v1.0/devices/{device_id}/status")["result"]

#Sends command to the device
def send_cmd(device_id, code, value):
    return api.post(f"/v1.0/devices/{device_id}/commands", 
                    {"commands": [{"code": code, "value": value}]})

##It monitors a specific device's status every 2 seconds
def monitor(device_id):
    info = get_info(device_id)
    print(f"\nMonitoring {info['name']} (Press Enter to stop)\n")
    
    stop = [False]
    threading.Thread(target=lambda: (input(), stop.__setitem__(0, True)), daemon=True).start()
    
    while not stop[0]:
        print("\033[H\033[J", end="")
        print(f"{info['name']} - {time.strftime('%H:%M:%S')}\n")
        for s in get_status(device_id):
            print(f"  {s['code']}: {s['value']}")
        time.sleep(2)
    print("\nStopped")

# Main
devices = get_devices()
print(f"\n{len(devices)} devices loaded\n")

while True:
    print("  1. List\n  2. Status\n  3. Command\n  4. Monitor\n  5. Exit")
    choice = input("-> ").strip()
    
    if choice == '1':
        for i, d in enumerate(devices, 1):
            info = get_info(d['id'])
            print(f"{i}. {info['name']} ({'ON' if info['online'] else 'OFF'})")
    
    elif choice in ['2', '3', '4']:
        num = input("Device #: ")
        if not num.isdigit() or not (1 <= int(num) <= len(devices)):
            continue
        
        device_id = devices[int(num)-1]['id']
        
        if choice == '4':
            monitor(device_id)
        else:
            info = get_info(device_id)
            status = get_status(device_id)
            
            print(f"\n{info['name']}:")
            for s in status:
                print(f"  {s['code']}: {s['value']}")
            
            if choice == '3':
                while True:
                    cmd = input("\ncode=value (or 'q'): ")
                    if cmd == 'q':
                        break
                    try:
                        code, val = cmd.split('=')
                        if val == 'true': val = True
                        elif val == 'false': val = False
                        elif val.isdigit(): val = int(val)
                        
                        if send_cmd(device_id, code, val).get("success"):
                            print("✓")
                    except:
                        print("✗")
    
    elif choice == '5':
        break
