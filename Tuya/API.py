from tuya_connector import TuyaOpenAPI

ACCESS_ID = "wq3f87vwvv8jpj5ynsqu"
ACCESS_KEY = "c1250567ba4a4361a85678c7431ba3c1"

openapi = TuyaOpenAPI("https://openapi.tuyaeu.com", ACCESS_ID, ACCESS_KEY)
openapi.connect()

# Get all devices
devices_response = openapi.get("/v2.0/cloud/thing/device?page_size=20")
devices = devices_response.get("result", [])

print(f"Found {len(devices)} device(s):\n")

for device in devices:
    # Get device details
    info = openapi.get(f"/v1.0/devices/{device['id']}")["result"]
    status = openapi.get(f"/v1.0/devices/{device['id']}/status")["result"]
    
    print(f"Device: {info['name']}")
    print(f"  ID: {device['id']}")
    print(f"  Online: {info['online']}")
    print(f"  Status:")
    for item in status:
        print(f"    {item['code']}: {item['value']}")
    print('\n')
