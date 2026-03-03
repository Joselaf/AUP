"""
Multi-Device Monitor with SQL Server Express 2022
Monitors all Tuya devices using tinytuya's cloud connection
Stores data in SQL Server Express database
"""

import tinytuya
import time
import threading
from datetime import datetime
import pyodbc

## Tuya Cloud credentials
ACCESS_ID = "c8uhx3vs89grhea8mg7p"
ACCESS_KEY = "7221603a3b754d8b89b30c8dc9114b0d"
REGION = "eu"  # Options: us, eu, cn, in

## SQL Server connection settings
SQL_SERVER = "localhost\\SQLEXPRESS"  # Change if your instance has different name
SQL_DATABASE = "DEVICES"
SQL_USERNAME = ""  # Leave empty for Windows Authentication
SQL_PASSWORD = ""  # Leave empty for Windows Authentication

## Initialize cloud connection
cloud = tinytuya.Cloud(
    apiRegion=REGION,
    apiKey=ACCESS_ID,
    apiSecret=ACCESS_KEY
)

## Get SQL Server connection
def get_connection():
    """Create connection to SQL Server"""
    try:
        if SQL_USERNAME and SQL_PASSWORD:
            # SQL Server Authentication
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};UID={SQL_USERNAME};PWD={SQL_PASSWORD}'
        else:
            # Windows Authentication
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};Trusted_Connection=yes;'
        
        conn = pyodbc.connect(conn_str, timeout=10)
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to SQL Server: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure SQL Server Express 2022 is running")
        print("2. Verify the server name (default: localhost\\SQLEXPRESS)")
        print("3. Check that 'devices' database exists")
        print("4. Install ODBC Driver: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
        return None

## Initialize database tables
def init_database():
    """Check if table exists"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if DeviceConsumptions table exists
        cursor.execute('''
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'dbo' 
            AND TABLE_NAME = 'DeviceConsumptions'
        ''')
        
        exists = cursor.fetchone()[0]
        
        if exists:
            print("Found existing table: dbo.DeviceConsumptions")
            cursor.close()
            conn.close()
            return True
        else:
            print("Table dbo.DeviceConsumptions not found!")
            print("Please create the table first or provide the table structure.")
            cursor.close()
            conn.close()
            return False
        
    except pyodbc.Error as e:
        print(f"Error checking database: {e}")
        conn.close()
        return False

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
        return []

## Save device info to database (not used if table structure is different)
def save_device_info(device_id, name, online):
    # This function may not be needed depending on your table structure
    pass

## Save monitoring data to database
def save_monitoring_data(device_id, device_name, power, current, voltage, energy, switch_state):
    conn = get_connection()
    if not conn:
        print(f"Failed to connect to database for saving data")
        return
    
    try:
        cursor = conn.cursor()
        
        # Insert into DeviceConsumptions table
        # Your table has: Id (auto), DeviceName, Consumption, ReadingDate
        # We'll use energy (kWh) as the consumption value
        cursor.execute('''
            INSERT INTO dbo.DeviceConsumptions 
            (DeviceName, Consumption, ReadingDate)
            VALUES (?, ?, ?)
        ''', (device_name, energy, datetime.now()))
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[{device_name}] Consumption: {energy} kWh saved to database")
        
    except pyodbc.Error as e:
        print(f"Error saving monitoring data: {e}")
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
                
                # Debug output
                print(f"[{device_name}] Power: {power}W, Current: {current}mA, Voltage: {voltage}V, Energy: {energy}kWh")
                
                save_monitoring_data(device_id, device_name, power, current, voltage, energy, switch_state)
                save_device_info(device_id, device_name, True)
                
            else:
                # No status received
                print(f"[{device_name}] No status data received")
                save_device_info(device_id, device_name, False)
                
        except Exception as e:
            print(f"[{device_name}] Error: {e}")
            save_device_info(device_id, device_name, False)
        
        time.sleep(60)  # Poll every 60 seconds (1 minute) instead of 5
    
    print(f"[{device_name}] Monitoring stopped")

## Start monitoring all devices
def start_monitoring():
    print("\n" + "=" * 60)
    print("SQL SERVER MULTI-DEVICE MONITORING")
    print("=" * 60)
    
    # Test database connection
    print("\nTesting SQL Server connection...")
    if not init_database():
        print("\nFailed to connect to SQL Server. Please check your configuration.")
        return
    
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
    print(f"Data is being saved to SQL Server: {SQL_SERVER}")
    print(f"Database: {SQL_DATABASE}")
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
        
        print("All monitors stopped. Data saved to SQL Server.")

## View device history
def view_history():
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get all unique devices
        cursor.execute('SELECT DISTINCT DeviceName FROM dbo.DeviceConsumptions ORDER BY DeviceName')
        devices = cursor.fetchall()
        
        if not devices:
            print("\nNo devices found in database. Run monitoring first.")
            cursor.close()
            conn.close()
            return
        
        print("\n" + "=" * 60)
        print("DEVICE HISTORY")
        print("=" * 60)
        print("\nAvailable devices:")
        for i, (device_name,) in enumerate(devices, 1):
            print(f"{i}. {device_name}")
        
        choice = input("\nSelect device number (or press Enter to cancel): ").strip()
        
        if not choice.isdigit() or not (1 <= int(choice) <= len(devices)):
            cursor.close()
            conn.close()
            return
        
        device_name = devices[int(choice) - 1][0]
        
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
                SELECT ReadingDate, Consumption
                FROM dbo.DeviceConsumptions
                WHERE DeviceName = ? AND ReadingDate >= DATEADD(hour, -1, GETDATE())
                ORDER BY ReadingDate DESC
            '''
        elif time_choice == '2':
            query = '''
                SELECT ReadingDate, Consumption
                FROM dbo.DeviceConsumptions
                WHERE DeviceName = ? AND ReadingDate >= DATEADD(day, -1, GETDATE())
                ORDER BY ReadingDate DESC
            '''
        elif time_choice == '3':
            query = '''
                SELECT ReadingDate, Consumption
                FROM dbo.DeviceConsumptions
                WHERE DeviceName = ? AND ReadingDate >= DATEADD(day, -7, GETDATE())
                ORDER BY ReadingDate DESC
            '''
        elif time_choice == '4':
            query = '''
                SELECT ReadingDate, Consumption
                FROM dbo.DeviceConsumptions
                WHERE DeviceName = ?
                ORDER BY ReadingDate DESC
            '''
        else:
            cursor.close()
            conn.close()
            return
        
        cursor.execute(query, device_name)
        records = cursor.fetchall()
        
        if not records:
            print("\nNo data found for this time range.")
            cursor.close()
            conn.close()
            return
        
        # Display statistics
        print(f"\n{device_name} - Statistics")
        print("=" * 80)
        
        consumptions = [r[1] for r in records if r[1] is not None]
        
        if consumptions:
            print(f"Consumption: Avg: {sum(consumptions)/len(consumptions):.4f} kWh  |  Max: {max(consumptions):.4f} kWh  |  Min: {min(consumptions):.4f} kWh")
        
        # Calculate energy consumed in period
        if len(records) > 1:
            first_energy = records[-1][1] or 0
            last_energy = records[0][1] or 0
            energy_used = last_energy - first_energy
            if energy_used > 0:
                print(f"Energy consumed in period: {energy_used:.4f} kWh")
        
        print(f"\nTotal records: {len(records)}")
        
        # Show recent data
        print("\nRecent readings (last 20):")
        print("-" * 60)
        print(f"{'Reading Date':<25} {'Consumption (kWh)':<20}")
        print("-" * 60)
        
        for record in records[:20]:
            reading_date, consumption = record
            date_str = reading_date.strftime('%Y-%m-%d %H:%M:%S')
            print(f"{date_str:<25} {consumption:<20.4f}")
        
        cursor.close()
        conn.close()
        
    except pyodbc.Error as e:
        print(f"Error: {e}")
        conn.close()

## View live status
def view_live_status():
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        print("\n" + "=" * 60)
        print("LIVE DEVICE STATUS")
        print("=" * 60)
        
        # Get latest reading for each device
        cursor.execute('''
            SELECT DeviceName, MAX(ReadingDate) as LastReading, 
                   (SELECT TOP 1 Consumption FROM dbo.DeviceConsumptions dc2 
                    WHERE dc2.DeviceName = dc1.DeviceName 
                    ORDER BY ReadingDate DESC) as LastConsumption
            FROM dbo.DeviceConsumptions dc1
            GROUP BY DeviceName
            ORDER BY DeviceName
        ''')
        
        devices = cursor.fetchall()
        
        if not devices:
            print("\nNo devices found. Run monitoring first.")
            cursor.close()
            conn.close()
            return
        
        print()
        for device in devices:
            name, last_reading, consumption = device
            
            print(f"{name}")
            if last_reading:
                print(f"  Last reading: {last_reading.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Consumption: {consumption:.4f} kWh")
            else:
                print(f"  No data available")
            print()
        
        cursor.close()
        conn.close()
        
    except pyodbc.Error as e:
        print(f"Error: {e}")
        conn.close()
    
    input("Press Enter to continue...")

## Main menu
def main():
    print("\n" + "=" * 60)
    print("SQL SERVER CONFIGURATION")
    print("=" * 60)
    print(f"Server: {SQL_SERVER}")
    print(f"Database: {SQL_DATABASE}")
    print(f"Authentication: {'SQL Server' if SQL_USERNAME else 'Windows'}")
    print("=" * 60)
    
    while True:
        print("\n" + "=" * 60)
        print("TUYA MULTI-DEVICE MONITOR (SQL Server)")
        print("=" * 60)
        print("1. Start monitoring all devices")
        print("2. View device history")
        print("3. View live status")
        print("4. Exit")
        
        choice = input("\n-> ").strip()
        
        if choice == '1':
            start_monitoring()
        elif choice == '2':
            view_history()
        elif choice == '3':
            view_live_status()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
