"""
Local network monitoring - Communicates directly with Tuya devices (FAST!)
No cloud API needed - all communication happens on your local network
"""

import tinytuya
import pyodbc
from datetime import datetime
import time
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
## Device configuration file
DEVICES_FILE = "devices.json"

## SQL Server settings
SQL_SERVER = "localhost\\SQLEXPRESS"
SQL_DATABASE = "Monitor"

## Polling interval (seconds)
POLL_INTERVAL = 5

## Global connection string
CONN_STR = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};Trusted_Connection=yes;'

## Load device configurations
def load_devices():
    """Load device configurations from JSON file"""
    if not os.path.exists(DEVICES_FILE):
        print("=" * 60)
        print("DEVICE CONFIGURATION NOT FOUND")
        print("=" * 60)
        print("\nYou need to create a 'devices.json' file with your device info.")
        print("\nQuick Setup:")
        print("1. pip install tinytuya")
        print("2. python -m tinytuya wizard")
        print("3. Follow the wizard - it will create devices.json automatically\n")
        print("Manual Setup - Create 'devices.json' with this format:")
        example = {
            "devices": [
                {
                    "name": "Smart Plug 1",
                    "id": "device_id_here",
                    "ip": "192.168.1.100",
                    "key": "local_key_here",
                    "version": "3.3"
                }
            ]
        }
        print(json.dumps(example, indent=2))
        print("\n" + "=" * 60)
        return []
    
    with open(DEVICES_FILE, 'r') as f:
        config = json.load(f)
    return config.get('devices', [])

## Create device connection
def create_device(device_config):
    """Create a tinytuya device object"""
    return tinytuya.OutletDevice(
        dev_id=device_config['id'],
        address=device_config['ip'],
        local_key=device_config['key'],
        version=float(device_config.get('version', '3.3'))
    )

## Database connection
def get_db_connection():
    """Create SQL Server connection"""
    try:
        return pyodbc.connect(CONN_STR, timeout=5)
    except pyodbc.Error:
        return None

## Batch insert to database
def batch_save_to_database(data_list):
    """Insert multiple records at once"""
    if not data_list:
        return 0
    
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor()
        cursor.fast_executemany = True
        
        cursor.executemany('''
            INSERT INTO dbo.DeviceLog (DeviceName, Consumption_kWh, ReadingTime)
            VALUES (?, ?, ?)
        ''', data_list)
        
        rows_affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return rows_affected
    except pyodbc.Error as e:
        print(f"  Batch insert error: {e}")
        conn.close()
        return 0

## Fetch single device data locally
def fetch_device_data_local(device_config):
    """Fetch status from device on local network"""
    device_name = device_config['name']
    start_time = time.time()
    
    try:
        device = create_device(device_config)
        
        # Get status from local device
        data = device.status()
        fetch_time = time.time() - start_time
        
        if not data or 'dps' not in data:
            return (device_name, 0, False, "No data", fetch_time)
        
        dps = data['dps']
        
        # Extract energy consumption
        # DPS codes: 17 = total energy (kWh*100), 19 = power (W*10)
        energy = 0
        
        # Try different DPS codes for energy
        if '17' in dps:
            energy = dps['17'] / 100
        elif 17 in dps:
            energy = dps[17] / 100
        
        return (device_name, energy, True, None, fetch_time)
        
    except Exception as e:
        fetch_time = time.time() - start_time
        return (device_name, 0, False, str(e), fetch_time)

## Main monitoring loop
def monitor_devices():
    """Continuously fetch and save device data"""
    print(f"\nLoading device configurations...")
    devices_config = load_devices()
    
    if not devices_config:
        print("No devices configured!")
        return
    
    device_count = len(devices_config)
    print(f"Found {device_count} device(s):\n")
    for i, device in enumerate(devices_config, 1):
        print(f"  {i}. {device['name']} ({device['ip']})")
    
    print(f"\nStarting LOCAL network monitoring (polling every {POLL_INTERVAL}s)...")
    print("All communication happens on your local network - FAST!")
    print("Press Ctrl+C to stop\n")
    
    cycle_count = 0
    total_saved = 0
    
    try:
        # Use thread pool for parallel device queries
        with ThreadPoolExecutor(max_workers=20) as executor:
            while True:
                cycle_count += 1
                cycle_start = time.time()
                timestamp = datetime.now()
                
                print(f"--- Cycle {cycle_count} [{timestamp.strftime('%H:%M:%S')}] ---")
                
                # Fetch all devices simultaneously
                fetch_start = time.time()
                futures = {executor.submit(fetch_device_data_local, device): device for device in devices_config}
                
                # Collect results and prepare batch insert
                batch_data = []
                results = []
                fetch_times = []
                
                collect_start = time.time()
                for future in as_completed(futures):
                    device_name, energy, success, error, fetch_time = future.result()
                    results.append((device_name, energy, success, error))
                    fetch_times.append(fetch_time)
                    
                    if success:
                        batch_data.append((device_name, energy, timestamp))
                collect_time = time.time() - collect_start
                
                # Batch insert all successful readings at once
                db_start = time.time()
                saved_count = batch_save_to_database(batch_data)
                db_time = time.time() - db_start
                total_saved += saved_count
                
                # Sort and display results
                results.sort(key=lambda x: x[0])
                
                success_count = 0
                for device_name, energy, success, error in results:
                    if success:
                        print(f"  ✓ {device_name}: {energy:.4f} kWh")
                        success_count += 1
                    else:
                        print(f"  ✗ {device_name}: {error}")
                
                elapsed = time.time() - cycle_start
                avg_fetch = sum(fetch_times) / len(fetch_times) if fetch_times else 0
                max_fetch = max(fetch_times) if fetch_times else 0
                
                print(f"  [Local API: avg {avg_fetch:.3f}s, max {max_fetch:.3f}s | DB: {db_time:.3f}s]")
                print(f"  [Total: {elapsed:.2f}s | {success_count}/{device_count} saved | Cycle total: {total_saved}]\n")
                
                # Sleep for remaining time
                sleep_time = max(0, POLL_INTERVAL - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        print(f"Cycles: {cycle_count} | Total records saved: {total_saved}")

## Run the script
if __name__ == "__main__":
    print("=" * 60)
    print("TUYA LOCAL NETWORK MONITOR - Direct Device Communication")
    print("=" * 60)
    print(f"Database: {SQL_SERVER} -> {SQL_DATABASE}")
    print(f"Table: dbo.DeviceLog")
    print(f"Polling: {POLL_INTERVAL}s | Mode: Local network (NO CLOUD)")
    print("=" * 60)
    
    # Test database connection
    print("\nTesting database connection...")
    conn = get_db_connection()
    if conn:
        print("✓ Database connection successful")
        conn.close()
        monitor_devices()
    else:
        print("✗ Database connection failed")
        print("\nCheck: SQL Server running, Database 'Monitor' exists, Table 'dbo.DeviceLog' exists")
