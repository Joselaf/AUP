"""
Fetch status of all devices in devices.json every 30 seconds
Uses get_dps.py to check device-specific alerts by category
"""

import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from regex import match
import tinytuya
from devices import *


DEVICES_FILE = "devices.json"
POLL_INTERVAL = 0

def load_devices():
    """Load devices from devices.json"""
    with open(DEVICES_FILE) as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get('devices', [])

def check_device(device):
    """Check a single device and return its alerts"""
    name = device.get('name', 'Unknown')
    category = device.get('category', 'unknown')
    ##alerts = get_alerts(device)
    return (name, category, alerts)

if __name__ == "__main__":

    devices = load_devices()
    ##valid = [d for d in devices if d.get('ip')]
    ##skipped = [d for d in devices if not d.get('ip')]
    
    devices_cat = {}    
    
    for d in devices:
        obj = tinytuya.OutletDevice(d['id'], d['ip'], d['key'])
        obj.set_version(d['version'])
        devices_cat[d['category']] = obj
    
    devices_type = {}
    
    
    for category, device in devices_cat.items():
        match category:
            case 'dlq':
                d = breaker(device['id'], device['ip'], device['key'], device['name'])
                devices_type[device['disjuntor']] = d
            
            case 'dlq'if("consumo" in device['name'].lower()):
                d = breaker(device['id'], device['ip'], device['key'], device['name'])
                devices_type[device['disjuntor_consumo']] = d
                
            case 'tdp':
                d = heater(device['id'], device['ip'], device['key'], device['name'])
                devices_type[device['aquecedor']] = d
                
            case 'mcs':
                d = contact_sensor(device['id'], device['ip'], device['key'], device['name'])
                devices_type[device['contact_sensor']] = d
                
            case 'hps':
                d = presence_sensor(device['id'], device['ip'], device['key'], device['name'])
                devices_type[device['presence_sensor']] = d
            
            case 'ms':
                d = smart_lock(device['id'], device['ip'], device['key'], device['name'])
                devices_type[device['fechadura_inteligente']] = d
            
            case 'cz':
                d = smart_plug(device['id'], device['ip'], device['key'], device['name'])
                devices_type[device['luz_estufa']] = d
            
            case 'dj'if("\u6b27\u7248A60-WB 9W RGBCW 220V E27" in device['name'].lower()):
                d = smart_bulb(device['id'], device['ip'], device['key'], device['name'])
                devices_type[device['luz_inteligente']] = d
            
            case 'dj'if("esmax" in device['name'].lower()):
                d = esmax(device['id'], device['ip'], device['key'], device['name'])
                devices_type[device['esmax']] = d
                
            case 'dj':
                d = smart_ir(device['id'], device['ip'], device['key'], device['name'])
                devices_type[device['ir']] = d
            
            case 'tv':
                d = smart_tv(device['id'], device['ip'], device['key'], device['name'])
                devices_type[device['tv']] = d
            
            
        
    
   
    
    

    try:
        while True:
      

            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(check_device, d) for d in valid]
                results = [f.result() for f in as_completed(futures)]

            # Sort by category then name
            results.sort(key=lambda x: (x[1], x[0]))

            for name, category ,alerts in results:
                for alert in alerts:
                    print(f"{name}:{alert}")
                

            
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n\nStopped.")
