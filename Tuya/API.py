from tuya_connector import TuyaOpenAPI
import time
import threading
import csv
from datetime import datetime
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
    
    # Create log files with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"device_log_{info['name'].replace(' ', '_')}_{timestamp}.csv"
    txt_filename = f"device_log_{info['name'].replace(' ', '_')}_{timestamp}.txt"
    
    stop = [False]
    threading.Thread(target=lambda: (input(), stop.__setitem__(0, True)), daemon=True).start()
    
    total_kwh = 0.0
    last_time = time.time()
    
    # Initialize CSV file
    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'code', 'value'])
    
    # Initialize text file
    with open(txt_filename, 'w') as f:
        f.write(f"Device Monitoring Log: {info['name']}\n")
        f.write("=" * 50 + "\n\n")
    
    print(f"Logging to: {csv_filename} and {txt_filename}\n")
    
    while not stop[0]:
        print("\033[H\033[J", end="")
        print(f"{info['name']} - {time.strftime('%H:%M:%S')}\n")
        
        status = get_status(device_id)
        consumption_data = {}
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for s in status:
            # Only process consumption-related metrics
            if s['code'] in ['cur_power', 'cur_current', 'cur_voltage', 'power', 'add_ele']:
                consumption_data[s['code']] = s['value']
        
        # Display as table
        print("┌─────────────────┬──────────────┐")
        print("│ Metric          │ Value        │")
        print("├─────────────────┼──────────────┤")
        
        table_lines = []
        table_lines.append("┌─────────────────┬──────────────┐")
        table_lines.append("│ Metric          │ Value        │")
        table_lines.append("├─────────────────┼──────────────┤")
        
        if 'cur_power' in consumption_data:
            power_w = consumption_data['cur_power'] / 10
            line = f"│ Power           │ {power_w:>9.1f} W │"
            print(line)
            table_lines.append(line)
        if 'cur_current' in consumption_data:
            line = f"│ Current         │ {consumption_data['cur_current']:>9} mA │"
            print(line)
            table_lines.append(line)
        if 'cur_voltage' in consumption_data:
            voltage_v = consumption_data['cur_voltage'] / 10
            line = f"│ Voltage         │ {voltage_v:>9.1f} V │"
            print(line)
            table_lines.append(line)
        if 'add_ele' in consumption_data:
            energy_kwh = consumption_data['add_ele'] / 100
            line = f"│ Total Energy    │ {energy_kwh:>9.2f} kWh│"
            print(line)
            table_lines.append(line)
        
        print("└─────────────────┴──────────────┘")
        table_lines.append("└─────────────────┴──────────────┘")
        
        # Save only consumption values to CSV file
        with open(csv_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            for code, value in consumption_data.items():
                writer.writerow([current_timestamp, code, value])
        
        # Calculate kWh consumption
        current_time = time.time()
        time_diff_hours = (current_time - last_time) / 3600
        
        if 'cur_power' in consumption_data:
            power_watts = consumption_data['cur_power'] / 10
            total_kwh += (power_watts / 1000) * time_diff_hours
            session_line = f"\nSession Energy: {total_kwh:.4f} kWh"
            print(session_line)
            
            # Save session energy to CSV file
            with open(csv_filename, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([current_timestamp, 'session_energy_kwh', total_kwh])
        
        # Save table format to text file
        with open(txt_filename, 'a') as f:
            f.write(f"\n{current_timestamp}\n")
            f.write('\n'.join(table_lines))
            if 'cur_power' in consumption_data:
                f.write(f"\nSession Energy: {total_kwh:.4f} kWh")
            f.write("\n\n")
        
        last_time = current_time
        
        time.sleep(2)
    print(f"\nStopped - Data saved to {csv_filename} and {txt_filename}")

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
