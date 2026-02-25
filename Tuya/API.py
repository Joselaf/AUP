from tuya_connector import TuyaOpenAPI
import time
import threading

ACCESS_ID = "c8uhx3vs89grhea8mg7p"
ACCESS_KEY = "7221603a3b754d8b89b30c8dc9114b0d"

openapi = TuyaOpenAPI("https://openapi.tuyaeu.com", ACCESS_ID, ACCESS_KEY)
openapi.connect()

def get_all_devices():
    devices, seen = [], set()
    print("Loading devices", end="", flush=True)
    
    for page in range(10):
        body = {"page_size": 20}
        if devices:
            body["last_id"] = devices[-1]['id']  # Changed from last_row_key to last_id
        
        response = openapi.get("/v2.0/cloud/thing/device", body)
        result = response.get("result", [])
        
        if not result:
            break
        
        new_count = 0
        for d in result:
            if d['id'] not in seen:
                seen.add(d['id'])
                devices.append(d)
                new_count += 1
        
        print(".", end="", flush=True)
        
        # Stop if no new devices or less than 20 (last page)
        if new_count == 0 or len(result) < 20:
            break
    
    print(f" {len(devices)} found!")
    return devices

def get_device_info(device_id):
    return openapi.get(f"/v1.0/devices/{device_id}")["result"]

def get_device_status(device_id):
    return openapi.get(f"/v1.0/devices/{device_id}/status")["result"]

def send_command(device_id, code, value):
    return openapi.post(f"/v1.0/devices/{device_id}/commands", 
                       {"commands": [{"code": code, "value": value}]})

def monitor_device(device_id):
    info = get_device_info(device_id)
    print(f"\n=== Monitoring {info['name']} === (Press Enter to stop)\n")
    
    stop = False
    threading.Thread(target=lambda: (input(), globals().update(stop=True)), daemon=True).start()
    
    while not stop:
        print("\033[H\033[J" + f"Time: {time.strftime('%H:%M:%S')}\n")
        for item in get_device_status(device_id):
            print(f"  {item['code']}: {item['value']}")
        time.sleep(2)
    print("\n✓ Stopped")

# Main
devices = get_all_devices()
print(f"\n✓ Found {len(devices)} devices")

while True:
    print("\n1. List  \n2. Status  \n3. Command  \n4. Monitor  \n5. Exit")
    choice = input("Choice: ").strip()
    
    if choice == '1':
        for i, d in enumerate(devices, 1):
            info = get_device_info(d['id'])
            print(f"{i}. {info['name']} - {'Online' if info['online'] else 'Offline'}")
    
    elif choice in ['2', '3', '4']:
        for i, d in enumerate(devices, 1):
            print(f"{i}. {get_device_info(d['id'])['name']}")
        
        num = input("Device #: ").strip()
        if not num.isdigit() or not (1 <= int(num) <= len(devices)):
            print("✗ Invalid")
            continue
        
        device_id = devices[int(num)-1]['id']
        
        if choice == '2':
            info = get_device_info(device_id)
            print(f"\n=== {info['name']} ===")
            for item in get_device_status(device_id):
                print(f"  {item['code']}: {item['value']}")
        
        elif choice == '3':
            print("\nAvailable commands:")
            for item in get_device_status(device_id):
                print(f"  {item['code']}: {item['value']}")
            
            while True:
                cmd = input("\nCommand (code=value or 'back'): ").strip()
                if cmd == 'back':
                    break
                try:
                    code, val = cmd.split('=')
                    val = val.strip()
                    if val == 'true': val = True
                    elif val == 'false': val = False
                    elif val.isdigit(): val = int(val)
                    
                    if send_command(device_id, code.strip(), val).get("success"):
                        print("✓ Sent")
                    else:
                        print("✗ Failed")
                except:
                    print("✗ Use: code=value")
        
        elif choice == '4':
            monitor_device(device_id)
    
    elif choice == '5':
        break
