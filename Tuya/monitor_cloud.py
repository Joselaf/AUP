"""
Multi-Device Monitor with TinyTuya Cloud API
Monitors all Tuya devices using tinytuya's cloud connection
"""

import tinytuya
import time
import threading
import sqlite3
from datetime import datetime
import json

## Tuya Cloud credentials
ACCESS_ID = "c8uhx3vs89grhea8mg7p"
ACCESS_KEY = "7221603a3b754d8b89b30c8dc9114b0d"
REGION = "eu"  # Options: us, eu, cn, in

## Database file
DB_FILE = "cloud_monitoring.db"
## Initialize cloud connection
cloud = tinytuya.Cloud(
    apiRegion=REGION,
    apiKey=ACCESS_ID,
    apiSecret=ACCESS_KEY
)

## Initialize database
def init_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            name TEXT,
            online INTEGER,
            last_seen TIMESTAMP
        )
    ''')
    
    # Create monitoring data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitoring_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            timestamp TIMESTAMP,
            power REAL,
            current REAL,
            voltage REAL,
            energy REAL,
            switch_state INTEGER,
            FOREIGN KEY (device_id) REFERENCES devices(device_id)
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_device_timestamp 
        ON monitoring_data(device_id, timestamp)
    ''')
    
    conn.commit()
    conn.close()

## Get all devices from cloud
def get_devices():
    try:
        devices = cloud.getdevices()
        if devices:
            return devices
        return []
    except Exception as e:
        print(f"Error getting devices: {e}")
        return []

## Get device status from cloud
def get_device_status(device_id):
    try:
        status = cloud.getstatus(device_id)
        if status and 'result' in status:
            return status['result']
        return []
    except Exception as e:
        print(f"Error getting status for {device_id}: {e}")
        return []

## Save device info to database
def save_device_info(device_id, name, online):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO devices (device_id, name, online, last_seen)
        VALUES (?, ?, ?, ?)
    ''', (device_id, name, 1 if online else 0, datetime.now()))
    conn.commit()
    conn.close()

## Save monitoring data to database
def save_monitoring_data(device_id, power, current, voltage, energy, switch_state):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO monitoring_data (device_id, timestamp, power, current, voltage, energy, switch_state)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (device_id, datetime.now(), power, current, voltage, energy, switch_state))
    conn.commit()
    conn.close()

## Monitor single device (runs in separate thread)
def monitor_device(device_id, device_name, stop_event):
    print(f"[{device_name}] Monitoring started")
    
    while not stop_event.is_set():
        try:
            status = get_device_status(device_id)
            
            if status:
                consumption_data = {}
                switch_state = None
                
                # Parse status data
                for item in status:
                    code = item.get('code', '')
                    value = item.get('value', 0)
                    
                    if code == 'cur_power':
                        consumption_data['power'] = value / 10  # Convert to W
                    elif code == 'cur_current':
                        consumption_data['current'] = value  # mA
                    elif code == 'cur_voltage':
                        consumption_data['voltage'] = value / 10  # Convert to V
                    elif code == 'add_ele':
                        consumption_data['energy'] = value / 100  # Convert to kWh
                    elif code == 'switch_1' or code == 'switch':
                        switch_state = 1 if value else 0
                
                # Save to database
                power = consumption_data.get('power', 0)
                current = consumption_data.get('current', 0)
                voltage = consumption_data.get('voltage', 0)
                energy = consumption_data.get('energy', 0)
                
                save_monitoring_data(device_id, power, current, voltage, energy, switch_state)
                save_device_info(device_id, device_name, True)
                
            else:
                # No status received
                save_device_info(device_id, device_name, False)
                
        except Exception as e:
            print(f"[{device_name}] Error: {e}")
            save_device_info(device_id, device_name, False)
        
        time.sleep(5)  # Poll every 5 seconds
    
    print(f"[{device_name}] Monitoring stopped")

## Start monitoring all devices
def start_monitoring():
    print("\n" + "=" * 60)
    print("CLOUD MULTI-DEVICE MONITORING (TinyTuya)")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    # Get all devices from cloud
    print("\nConnecting to Tuya Cloud...")
    devices = get_devices()
    
    if not devices:
        print("No devices found or connection failed.")
        print("Check your credentials and internet connection.")
        return
    
    print(f"Found {len(devices)} device(s)")
    
    threads = []
    stop_event = threading.Event()
    
    # Start monitoring thread for each device
    for device in devices:
        device_id = device.get('id')
        device_name = device.get('name', 'Unknown')
        
        print(f"Starting monitor for: {device_name}")
        
        # Save device info
        save_device_info(device_id, device_name, device.get('online', False))
        
        # Create and start thread
        thread = threading.Thread(
            target=monitor_device,
            args=(device_id, device_name, stop_event),
            daemon=True
        )
        thread.start()
        threads.append(thread)
    
    print("\n" + "=" * 60)
    print("All devices are being monitored!")
    print("Data is being saved to database: " + DB_FILE)
    print("Press Ctrl+C to stop monitoring")
    print("=" * 60 + "\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping all monitors...")
        stop_event.set()
        
        # Wait for all threads to finish
        for thread in threads:
            thread.join(timeout=2)
        
        print("All monitors stopped. Data saved to database.")

## View device history
def view_history():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get all devices
    cursor.execute('SELECT device_id, name FROM devices ORDER BY name')
    devices = cursor.fetchall()
    
    if not devices:
        print("\nNo devices found in database. Run monitoring first.")
        conn.close()
        return
    
    print("\n" + "=" * 60)
    print("DEVICE HISTORY")
    print("=" * 60)
    print("\nAvailable devices:")
    for i, (device_id, name) in enumerate(devices, 1):
        print(f"{i}. {name}")
    
    choice = input("\nSelect device number (or press Enter to cancel): ").strip()
    
    if not choice.isdigit() or not (1 <= int(choice) <= len(devices)):
        conn.close()
        return
    
    device_id, device_name = devices[int(choice) - 1]
    
    # Get time range options
    print(f"\n{device_name} - History Options:")
    print("1. Last hour")
    print("2. Last 24 hours")
    print("3. Last 7 days")
    print("4. All time")
    
    time_choice = input("\nSelect option: ").strip()
    
    # Build query based on time range
    if time_choice == '1':
        query = '''
            SELECT timestamp, power, current, voltage, energy, switch_state
            FROM monitoring_data
            WHERE device_id = ? AND timestamp >= datetime('now', '-1 hour')
            ORDER BY timestamp DESC
        '''
    elif time_choice == '2':
        query = '''
            SELECT timestamp, power, current, voltage, energy, switch_state
            FROM monitoring_data
            WHERE device_id = ? AND timestamp >= datetime('now', '-1 day')
            ORDER BY timestamp DESC
        '''
    elif time_choice == '3':
        query = '''
            SELECT timestamp, power, current, voltage, energy, switch_state
            FROM monitoring_data
            WHERE device_id = ? AND timestamp >= datetime('now', '-7 days')
            ORDER BY timestamp DESC
        '''
    elif time_choice == '4':
        query = '''
            SELECT timestamp, power, current, voltage, energy, switch_state
            FROM monitoring_data
            WHERE device_id = ?
            ORDER BY timestamp DESC
        '''
    else:
        conn.close()
        return
    
    cursor.execute(query, (device_id,))
    records = cursor.fetchall()
    
    if not records:
        print("\nNo data found for this time range.")
        conn.close()
        return
    
    # Display statistics
    print(f"\n{device_name} - Statistics")
    print("=" * 80)
    
    powers = [r[1] for r in records if r[1] is not None and r[1] > 0]
    currents = [r[2] for r in records if r[2] is not None and r[2] > 0]
    voltages = [r[3] for r in records if r[3] is not None and r[3] > 0]
    
    if powers:
        print(f"Power:   Avg: {sum(powers)/len(powers):.1f} W  |  Max: {max(powers):.1f} W  |  Min: {min(powers):.1f} W")
    if currents:
        print(f"Current: Avg: {sum(currents)/len(currents):.0f} mA  |  Max: {max(currents):.0f} mA  |  Min: {min(currents):.0f} mA")
    if voltages:
        print(f"Voltage: Avg: {sum(voltages)/len(voltages):.1f} V  |  Max: {max(voltages):.1f} V  |  Min: {min(voltages):.1f} V")
    
    # Calculate energy consumption
    if len(records) > 1:
        first_energy = records[-1][4] or 0
        last_energy = records[0][4] or 0
        energy_used = last_energy - first_energy
        if energy_used > 0:
            print(f"Energy consumed in period: {energy_used:.3f} kWh")
    
    print(f"\nTotal records: {len(records)}")
    
    # Show recent data
    print("\nRecent readings (last 10):")
    print("-" * 90)
    print(f"{'Timestamp':<20} {'Power (W)':<12} {'Current (mA)':<15} {'Voltage (V)':<12} {'Energy (kWh)':<12} {'State':<8}")
    print("-" * 90)
    
    for record in records[:10]:
        timestamp, power, current, voltage, energy, switch_state = record
        state = "ON" if switch_state == 1 else "OFF" if switch_state == 0 else "N/A"
        print(f"{timestamp:<20} {power or 0:<12.1f} {current or 0:<15.0f} {voltage or 0:<12.1f} {energy or 0:<12.3f} {state:<8}")
    
    # Export option
    export = input("\nExport to CSV? (y/n): ").strip().lower()
    if export == 'y':
        filename = f"export_{device_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Timestamp,Power (W),Current (mA),Voltage (V),Energy (kWh),Switch State\n")
            for record in records:
                state = "ON" if record[5] == 1 else "OFF" if record[5] == 0 else "N/A"
                f.write(f"{record[0]},{record[1] or 0},{record[2] or 0},{record[3] or 0},{record[4] or 0},{state}\n")
        print(f"Data exported to: {filename}")
    
    conn.close()

## View live status
def view_live_status():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("LIVE DEVICE STATUS")
    print("=" * 60)
    
    # Get latest reading for each device
    cursor.execute('''
        SELECT d.name, d.online, d.last_seen,
               m.power, m.current, m.voltage, m.energy, m.switch_state
        FROM devices d
        LEFT JOIN monitoring_data m ON d.device_id = m.device_id
        WHERE m.timestamp = (
            SELECT MAX(timestamp) 
            FROM monitoring_data 
            WHERE device_id = d.device_id
        )
        OR m.timestamp IS NULL
        ORDER BY d.name
    ''')
    
    devices = cursor.fetchall()
    
    if not devices:
        print("\nNo devices found. Run monitoring first.")
        conn.close()
        return
    
    print()
    for device in devices:
        name, online, last_seen, power, current, voltage, energy, switch_state = device
        status = "ONLINE" if online else "OFFLINE"
        state = "ON" if switch_state == 1 else "OFF" if switch_state == 0 else "N/A"
        
        print(f"{name} - {status}")
        print(f"  Last seen: {last_seen}")
        if power is not None:
            print(f"  Power: {power:.1f} W  |  Current: {current:.0f} mA  |  Voltage: {voltage:.1f} V")
            print(f"  Energy: {energy:.3f} kWh  |  Switch: {state}")
        else:
            print(f"  No data available")
        print()
    
    conn.close()
    input("Press Enter to continue...")

## List all devices
def list_devices():
    print("\n" + "=" * 60)
    print("AVAILABLE DEVICES")
    print("=" * 60)
    
    print("\nFetching devices from cloud...")
    devices = get_devices()
    
    if not devices:
        print("No devices found or connection failed.")
        return
    
    print(f"\nFound {len(devices)} device(s):\n")
    
    for i, device in enumerate(devices, 1):
        device_id = device.get('id')
        device_name = device.get('name', 'Unknown')
        online = device.get('online', False)
        status = "ONLINE" if online else "OFFLINE"
        
        print(f"{i}. {device_name}")
        print(f"   ID: {device_id}")
        print(f"   Status: {status}")
        print()
    
    input("Press Enter to continue...")

## Main menu
def main():
    while True:
        print("\n" + "=" * 60)
        print("TUYA CLOUD MULTI-DEVICE MONITOR (TinyTuya)")
        print("=" * 60)
        print("1. Start monitoring all devices")
        print("2. View device history")
        print("3. View live status")
        print("4. List all devices")
        print("5. Exit")
        
        choice = input("\n-> ").strip()
        
        if choice == '1':
            start_monitoring()
        elif choice == '2':
            view_history()
        elif choice == '3':
            view_live_status()
        elif choice == '4':
            list_devices()
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
