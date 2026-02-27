from tuya_connector import TuyaOpenAPI
import time
import threading
from datetime import datetime

## Tuya IoT Platform credentials
ACCESS_ID = "c8uhx3vs89grhea8mg7p"
ACCESS_KEY = "7221603a3b754d8b89b30c8dc9114b0d"

## Connect to API
api = TuyaOpenAPI("https://openapi.tuyaeu.com", ACCESS_ID, ACCESS_KEY)
api.connect()

## Fetch all devices
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

## Get device info
def get_info(device_id):
    return api.get(f"/v1.0/devices/{device_id}")["result"]

## Get device status
def get_status(device_id):
    return api.get(f"/v1.0/devices/{device_id}/status")["result"]

## Monitor device consumption
def monitor(device_id):
    info = get_info(device_id)
    print(f"\nMonitoring {info['name']} (Press Enter to stop)\n")
    
    # Create log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"device_log_{info['name'].replace(' ', '_')}_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"Device Monitoring Log: {info['name']}\n")
        f.write("=" * 50 + "\n\n")
    
    print(f"Logging to: {filename}\n")
    
    stop = [False]
    threading.Thread(target=lambda: (input(), stop.__setitem__(0, True)), daemon=True).start()
    
    total_kwh = 0.0
    last_time = time.time()
    
    while not stop[0]:
        print("\033[H\033[J", end="")
        print(f"{info['name']} - {time.strftime('%H:%M:%S')}\n")
        
        status = get_status(device_id)
        consumption_data = {}
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for s in status:
            if s['code'] in ['cur_power', 'cur_current', 'cur_voltage', 'add_ele']:
                consumption_data[s['code']] = s['value']
        
        # Display table
        print("┌─────────────────┬──────────────┐")
        print("│ Metric          │ Value        │")
        print("├─────────────────┼──────────────┤")
        
        table_lines = []
        table_lines.append("┌─────────────────┬──────────────┐")
        table_lines.append("│ Metric          │ Value        │")
        table_lines.append("├─────────────────┼──────────────┤")
        
        if 'cur_power' in consumption_data:
            power_w = consumption_data['cur_power'] / 10
            line = f"│ Power           │ {power_w:>9.1f} W  │"
            print(line)
            table_lines.append(line)
        if 'cur_current' in consumption_data:
            line = f"│ Current         │ {consumption_data['cur_current']:>9} mA  │"
            print(line)
            table_lines.append(line)
        if 'cur_voltage' in consumption_data:
            voltage_v = consumption_data['cur_voltage'] / 10
            line = f"│ Voltage         │ {voltage_v:>9.1f} V  │"
            print(line)
            table_lines.append(line)
        if 'add_ele' in consumption_data:
            energy_kwh = consumption_data['add_ele'] / 100
            line = f"│ Total Energy    │ {energy_kwh:>9.2f} kWh│"
            print(line)
            table_lines.append(line)
        
        print("└─────────────────┴──────────────┘")
        table_lines.append("└─────────────────┴──────────────┘")
        
        # Calculate session energy
        current_time = time.time()
        time_diff_hours = (current_time - last_time) / 3600
        
        if 'cur_power' in consumption_data:
            power_watts = consumption_data['cur_power'] / 10
            total_kwh += (power_watts / 1000) * time_diff_hours
            print(f"\nSession Energy: {total_kwh:.4f} kWh")
        
        # Save to file
        with open(filename, 'a') as f:
            f.write(f"\n{current_timestamp}\n")
            f.write('\n'.join(table_lines))
            if 'cur_power' in consumption_data:
                f.write(f"\nSession Energy: {total_kwh:.4f} kWh")
            f.write("\n\n")
        
        last_time = current_time
        time.sleep(2)
    
    print(f"\nStopped - Data saved to {filename}")

## View device history from Tuya API
def view_history(device_id):
    info = get_info(device_id)
    print(f"\n{info['name']} - Energy History\n")

    print("Unfortunately, Tuya Cloud historical data APIs require:")
    print("  - Paid Tuya Cloud Development subscription")
    print("  - Special API permissions and configuration")
    print("  - Service ticket submission to Tuya")
    print("\nThese APIs are not available with standard free accounts.")
    print("\nAlternative: Use the Monitor feature to collect data locally,")
    print("which you can view anytime in the saved log files.")

    # Show local log files if available
    import glob
    import os

    device_name = info['name'].replace(' ', '_')
    log_files = glob.glob(f"device_log_{device_name}_*.txt")

    if log_files:
        log_files.sort(key=os.path.getmtime, reverse=True)

        print(f"\n\nLocal monitoring logs for {info['name']}:")
        print("─" * 60)
        for i, log_file in enumerate(log_files, 1):
            file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            file_size = os.path.getsize(log_file)
            print(f"{i}. {log_file}")
            print(f"   Created: {file_time.strftime('%Y-%m-%d %H:%M:%S')} ({file_size} bytes)")

        choice = input("\nEnter number to view log (or press Enter to skip): ").strip()

        if choice.isdigit():
            log_num = int(choice)
            if 1 <= log_num <= len(log_files):
                print(f"\n{'='*60}")
                with open(log_files[log_num-1], 'r') as f:
                    content = f.read()
                    print(content)
                print(f"{'='*60}")
    else:
        print(f"\n\nNo local logs found for {info['name']}")
        print("Use option 2 (Monitor Device) to start collecting data")

    input("\nPress Enter to continue...")







# Main
devices = get_devices()
for i, d in enumerate(devices, 1):
    info = get_info(d['id'])
    print(f"{i}. {info['name']} ({'ON' if info['online'] else 'OFF'})")
print(f"\n{len(devices)} devices loaded\n")

while True:
    print("  1. Monitor Device")
    print("  2. View History")
    print("  3. Exit")
    
    choice = input("-> ").strip()
    
    
    if choice in ['1', '2']:
        num = input("Device #: ")
        if not num.isdigit() or not (1 <= int(num) <= len(devices)):
            continue
        
        device_id = devices[int(num)-1]['id']
        
        if choice == '1':
            monitor(device_id)
        elif choice == '2':
            view_history(device_id)
    
    elif choice == '3':
        break
