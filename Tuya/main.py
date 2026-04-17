import json
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# Ensure the Tuya directory is on the path regardless of where script is run from
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tinytuya
from devices import *

DEVICES_FILE = "devices.json"

def load_devices():
    """Load devices from devices.json"""
    with open(DEVICES_FILE) as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get('devices', [])


def table(data: dict):
    """Print a status dict as a simple aligned table."""
    if data:
        print("ONLLINE")
        for key, value in data.items():
            print(f"  {key:<25} {value}")
    else:
        print("OFFLINE")

device_by_room = defaultdict(list)

def devices_by_room(device):
    d_name = device['name']
    for i in range(1, 27):
        if f"Q{i:02}" in d_name:
            device_by_room[f"Q{i:02}"].append(device)  # store with same padding used to match
            
def print_devices_by_room(room):
    """Print all devices in a room"""
    devices = device_by_room[room]
    for device in devices:
        print(device['name'])
        table(devices_status(device))
        print()

def devices_status(d):
            category = d['category']
            match category:
                case 'dlq':
                    if(not d['ip']):
                        return None
                    else:
                        d = breaker(device['id'], device['ip'], device['key'], device['name'])
                        return d.get_status()
                    
                case 'dlq'if("consumo" in device['name'].lower()):
                    if not d['ip']:
                        return None
                    else:      
                        d = consumption_breaker(device['id'], device['ip'], device['key'], device['name'])
                        return d.get_status()
                    
                case 'kg':
                    if not d['ip']:
                        return None
                    else:
                        d = breaker(device['id'], device['ip'], device['key'], device['name'])
                        return d.get_status()
                    
                case 'tdp':
                    if not d['ip']:
                            return None
                    else:
                        d = heater(device['id'], device['ip'], device['key'], device['name'])
                        return d.get_status()
                case 'mcs':
                    if not d['ip']:
                        return None
                    else:             
                        d = contact_sensor(device['id'], device['ip'], device['key'], device['name'])
                        return d.get_status()
                        
                case 'hps':
                    if not d['ip']:
                        return None
                    else:
                        d = presence_sensor(device['id'], device['ip'], device['key'], device['name'])
                        return d.get_status()
                
                case 'ms':
                    if not d['ip']:
                        return None
                    else:
                        d = lock(device['id'], device['ip'], device['key'], device['name'])
                        return d.get_status()
                
                case 'cz':
                    if not d['ip']:
                        return None
                    else:
                        d = smart_plug(device['id'], device['ip'], device['key'], device['name'])
                        return d.get_status()
                
                case 'dj'if("\u6b27\u7248A60-WB 9W RGBCW 220V E27" in device['name'].upper()):
                    if not d['ip']:
                        return None
                        d = smart_bulb(device['id'], device['ip'], device['key'], device['name'])
                        return d.get_status()
                
                case 'dj'if("esmax" in device['name'].lower()):
                    if not d['ip']:
                        return None
                    else:
                        d = esmax(device['id'], device['ip'], device['key'], device['name'])
                        return d.get_status()
                    
                case 'dj':
                    if not d['ip']:
                        return None
                    else:
                        d = smart_ir(device['id'], device['ip'], device['key'], device['name'])
                        return d.get_status()
                
                case 'tv':
                    if not d['ip']:
                        return None
                    else:
                        d = smart_tv(device['id'], device['ip'], device['key'], device['name'])
                        return d.get_status()
                    
                case 'jtmspro':
                    if not d['ip']:
                        return None
                    else:
                        d = smart_lock(device['id'], device['ip'], device['key'], device['name'])
                        return d.get_status()

if __name__ == "__main__":
    devices = load_devices()
    print("Finished loading file")
    
    try:
        with  ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(devices_by_room, device) for device in devices]
            for future in as_completed(futures):
                result = future.result()
    except Exception as e:
        print(f"Error in thread execution: {e}")
        
    print("Finished devices_by_room")

    for room, room_devices in device_by_room.items():
        print(f"\n{room}:")
        for device in room_devices:
            print(f"  {device['name']} - {device['id']}")
    
    valid_rooms = sorted(device_by_room.keys())
    print(f"\nQuartos disponíveis: {', '.join(valid_rooms)}")

    try:
        while True:
            room = int(input("\nEscolhe quarto para visualização: "))
            format_room = f"Q{room:02}"
            if format_room not in device_by_room:
                print(f"Quarto {format_room} não existe. Disponíveis: {', '.join(valid_rooms)}")
            else:
                print()
                print_devices_by_room(format_room)
    except KeyboardInterrupt:
        print("\nloop ended")
    
    
    
    
    

