from tuya_connector import TuyaOpenAPI

ACCESS_ID = "wq3f87vwvv8jpj5ynsqu"
ACCESS_KEY = "c1250567ba4a4361a85678c7431ba3c1"

openapi = TuyaOpenAPI("https://openapi.tuyaeu.com", ACCESS_ID, ACCESS_KEY)
result = openapi.connect()

if result.get("success"):
    print("✓ Connected successfully!\n")
    
    # Get all devices in the project
    devices_response = openapi.get("/v2.0/cloud/thing/device?page_size=20")
    
    if devices_response.get("success"):
        devices = devices_response["result"]
        print(f"Found {len(devices)} device(s):\n")
        
        for device in devices:
            device_id = device['id']
            
            # Get full device info to get the proper name
            info_response = openapi.get(f"/v1.0/devices/{device_id}")
            
            if info_response.get("success"):
                device_info = info_response["result"]
                device_name = device_info.get('name', 'Unknown')
                is_online = device_info.get('online', False)
            else:
                device_name = device.get('name', device.get('custom_name', 'Unknown'))
                is_online = 'N/A'
            
            print(f"Device: {device_name}")
            print(f"  ID: {device_id}")
            print(f"  Online: {is_online}")
            print(f"  Category: {device.get('category', 'N/A')}")
            print(f"  Product ID: {device.get('product_id', 'N/A')}")
            
            # Get device status
            status_response = openapi.get(f"/v1.0/devices/{device['id']}/status")
            if status_response.get("success"):
                print(f"  Status:")
                for item in status_response["result"]:
                    print(f"    {item['code']}: {item['value']}")
            else:
                print(f"  Status error: {status_response.get('msg')}")
            
    else:
        print(f"Error getting devices: {devices_response.get('msg')}")
else:
    print(f"✗ Connection failed: {result.get('msg')}")