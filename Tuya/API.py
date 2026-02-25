from tuya_connector import TuyaOpenAPI
import time
import threading
import sys

ACCESS_ID = "wq3f87vwvv8jpj5ynsqu"
ACCESS_KEY = "c1250567ba4a4361a85678c7431ba3c1"

openapi = TuyaOpenAPI("https://openapi.tuyaeu.com", ACCESS_ID, ACCESS_KEY)
openapi.connect()

def get_devices():
    devices_response = openapi.get("/v2.0/cloud/thing/device?page_size=20")
    return devices_response.get("result", [])

def show_devices(devices):
    print("\n=== Your Devices ===")
    for i, device in enumerate(devices, 1):
        info = openapi.get(f"/v1.0/devices/{device['id']}")["result"]
        print(f"{i}. {info['name']} (ID: {device['id']}) - {'Online' if info['online'] else 'Offline'}")

def show_device_status(device_id):
    info = openapi.get(f"/v1.0/devices/{device_id}")["result"]
    status = openapi.get(f"/v1.0/devices/{device_id}/status")["result"]
    
    print(f"\n=== {info['name']} Status ===")
    for item in status:
        print(f"  {item['code']}: {item['value']}")

def monitor_device(device_id):
    info = openapi.get(f"/v1.0/devices/{device_id}")["result"]
    print(f"\n=== Monitoring {info['name']} ===")
    print("Press 'q' and Enter to stop monitoring\n")
    
    stop_monitoring = False
    
    def check_input():
        nonlocal stop_monitoring
        input()
        stop_monitoring = True
    
    # Start input thread
    input_thread = threading.Thread(target=check_input, daemon=True)
    input_thread.start()
    
    try:
        while not stop_monitoring:
            status = openapi.get(f"/v1.0/devices/{device_id}/status")["result"]
            
            # Clear previous output
            print("\033[H\033[J", end="")
            print(f"=== Monitoring {info['name']} === (Press Enter to stop)\n")
            print(f"Time: {time.strftime('%H:%M:%S')}\n")
            
            for item in status:
                print(f"  {item['code']}: {item['value']}")
            
            time.sleep(2)  # Update every 2 seconds
    except KeyboardInterrupt:
        pass
    
    print("\n✓ Monitoring stopped")

def send_command(device_id):
    # Show current status first
    info = openapi.get(f"/v1.0/devices/{device_id}")["result"]
    status = openapi.get(f"/v1.0/devices/{device_id}/status")["result"]
    
    print(f"\n=== {info['name']} - Available Commands ===")
    print("Current status (these are the codes you can control):")
    for item in status:
        print(f"  {item['code']}: {item['value']}")
    
    print("\nEnter command (format: code=value, e.g., switch_1=true or percent_control=50)")
    print("Type 'back' to return")
    
    while True:
        cmd = input("\nCommand: ").strip()
        if cmd.lower() == 'back':
            break
        
        try:
            code, value = cmd.split('=')
            code = code.strip()
            value = value.strip()
            
            # Convert value to appropriate type
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            
            commands = {"commands": [{"code": code, "value": value}]}
            response = openapi.post(f"/v1.0/devices/{device_id}/commands", commands)
            
            if response.get("success"):
                print("✓ Command sent successfully!")
            else:
                print(f"✗ Error: {response.get('msg')}")
        except:
            print("✗ Invalid format. Use: code=value")

# Main menu
devices = get_devices()
print(f"\n✓ Connected! Found {len(devices)} device(s)")

while True:
    print("\n=== Main Menu ===")
    print("1. List devices")
    print("2. View device status")
    print("3. Send command")
    print("4. Monitor device (live updates)")
    print("5. Exit")
    
    choice = input("\nChoice: ").strip()
    
    if choice == '1':
        show_devices(devices)
    
    elif choice == '2':
        show_devices(devices)
        device_num = input("\nSelect device number: ").strip()
        if device_num.isdigit() and 1 <= int(device_num) <= len(devices):
            show_device_status(devices[int(device_num)-1]['id'])
        else:
            print("✗ Invalid device number")
    
    elif choice == '3':
        show_devices(devices)
        device_num = input("\nSelect device number: ").strip()
        if device_num.isdigit() and 1 <= int(device_num) <= len(devices):
            send_command(devices[int(device_num)-1]['id'])
        else:
            print("✗ Invalid device number")
    
    elif choice == '4':
        show_devices(devices)
        device_num = input("\nSelect device number: ").strip()
        if device_num.isdigit() and 1 <= int(device_num) <= len(devices):
            monitor_device(devices[int(device_num)-1]['id'])
        else:
            print("✗ Invalid device number")
    
    elif choice == '5':
        print("\nGoodbye!")
        break
    
    else:
        print("✗ Invalid choice")
