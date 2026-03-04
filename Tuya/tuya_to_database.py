"""
Simple script to fetch Tuya device data and populate SQL Server database
"""

import tinytuya
import pyodbc
from datetime import datetime
import time

## Tuya Cloud credentials
ACCESS_ID = "c8uhx3vs89grhea8mg7p"
ACCESS_KEY = "7221603a3b754d8b89b30c8dc9114b0d"
REGION = "eu"

## SQL Server settings
SQL_SERVER = "localhost\\SQLEXPRESS"
SQL_DATABASE = "Monitor"
SQL_TABLE = "dbo.DeviceLog"

## Polling interval (seconds)
POLL_INTERVAL = 1  # Fetch data every 60 seconds

## Connect to Tuya Cloud
print("Connecting to Tuya Cloud...")
cloud = tinytuya.Cloud(
    apiRegion=REGION,
    apiKey=ACCESS_ID,
    apiSecret=ACCESS_KEY
)

## Connect to SQL Server
def get_db_connection():
    """Create SQL Server connection"""
    try:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str, timeout=10)
        return conn
    except pyodbc.Error as e:
        print(f"Database connection error: {e}")
        return None

## Get all devices from Tuya
def get_devices():
    """Fetch all devices from Tuya Cloud"""
    try:
        devices = cloud.getdevices()
        return devices if devices else []
    except Exception as e:
        print(f"Error fetching devices: {e}")
        return []

## Get device status
def get_device_status(device_id):
    """Get current status of a device"""
    try:
        status = cloud.getstatus(device_id)
        return status.get('result', []) if status else []
    except Exception as e:
        return []

## Save data to database
def save_to_database(device_name, consumption):
    """Insert data into SQL Server"""
    conn = get_db_connection()
    if not conn:
        print(f"  Error: Could not connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Insert into DeviceLog table with correct column names
        cursor.execute('''
            INSERT INTO dbo.DeviceLog (DeviceName, Consumption_kWh, ReadingTime)
            VALUES (?, ?, ?)
        ''', (device_name, consumption, datetime.now()))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except pyodbc.Error as e:
        print(f"  *** DATABASE ERROR ***")
        print(f"  Error Code: {e.args[0]}")
        print(f"  Error Message: {e.args[1]}")
        print(f"  Device: {device_name}")
        print(f"  Consumption: {consumption}")
        
        conn.close()
        return False

## Main monitoring loop
def monitor_devices():
    """Continuously fetch and save device data"""
    print(f"\nFetching devices from Tuya Cloud...")
    devices = get_devices()
    
    if not devices:
        print("No devices found!")
        return
    
    print(f"Found {len(devices)} device(s):\n")
    for i, device in enumerate(devices, 1):
        print(f"  {i}. {device.get('name', 'Unknown')}")
    
    print(f"\nStarting monitoring (polling every {POLL_INTERVAL} seconds)...")
    print("Press Ctrl+C tovice.get('name', 'Unknown')}")
    
    print(f"\nStarting monitoring (polling every {POLL_INTERVAL} seconds)...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            for device in devices:
                device_id = device.get('id')
                device_name = device.get('name', 'Unknown')
                
                # Get device status
                status = get_device_status(device_id)
                
                if status:
                    # Extract energy consumption
                    energy = 0
                    for item in status:
                        code = item.get('code', '')
                        value = item.get('value', 0)
                        
                        if code == 'add_ele':  # Total energy in kWh*100
                            energy = value / 100
                            break
                    
                    # Save to database
                    if save_to_database(device_name, energy):
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {device_name}: {energy:.4f} kWh - Saved")
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {device_name}: Failed to save")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {device_name}: No data")
            
            # Wait before next poll
            time.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

## Run the script
if __name__ == "__main__":
    print("=" * 60)
    print("TUYA TO DATABASE - Simple Monitor")
    print("=" * 60)
    print(f"Database: {SQL_SERVER} -> {SQL_DATABASE}")
    print(f"Table: {SQL_TABLE}")
    print("=" * 60)
    
    # Test database connection
    print("\nTesting database connection...")
    conn = get_db_connection()
    if conn:
        print("✓ Database connection successful")
        conn.close()
        
        # Start monitoring
        monitor_devices()
    else:
        print("✗ Database connection failed")
        print("\nPlease check:")
        print("1. SQL Server is running")
        print("2. Database 'Monitor' exists")
        print("3. Table 'dbo.monitor' exists with columns: DeviceName, Consumption, ReadingDate")
