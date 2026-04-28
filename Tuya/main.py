import json
import sys
import os
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from devices import *
from is_device_reachable import is_device_reachable, is_expected_mac
    

def devices_status(device):
    ip = device.get('ip')
    expected_mac = device.get('mac')

    if not is_device_reachable(ip):
        return None

    # TinyTuya wizard data can become stale; reject IPs now owned by another host.
    if expected_mac and not is_expected_mac(ip, expected_mac):
        return None

    else: 
        category = device.get('category')
        match category:
            case 'dlq'if("consumo" in device['name'].lower()):
                if device['ip']:
                    return consumption_breaker(device['id'], device['ip'], device['key'], device['name'])
            case 'dlq':
                if device['ip']:
                    return breaker(device['id'], device['ip'], device['key'], device['name'])
            case 'kg':
                if device['ip']:
                    return breaker(device['id'], device['ip'], device['key'], device['name'])
            case 'tdp':
                if device['ip']:
                    return heater(device['id'], device['ip'], device['key'], device['name'])
            case 'mcs':
                if device['ip']:
                    return contact_sensor(device['id'], device['ip'], device['key'], device['name'])
                    
            case 'hps':
                if device['ip']:
                    return presence_sensor(device['id'], device['ip'], device['key'], device['name'])
            case 'ms':
                if device['ip']:
                    return lock(device['id'], device['ip'], device['key'], device['name'])
            case 'cz':
                if device['ip']:
                    return smart_plug(device['id'], device['ip'], device['key'], device['name'])
            case 'dj'if("\u6b27\u7248A60-WB 9W RGBCW 220V E27" in device['name'].upper()):
                if device['ip']:
                    return smart_bulb(device['id'], device['ip'], device['key'], device['name'])
            case 'dj'if("esmax" in device['name'].lower()):
                if device['ip']:
                    return esmax(device['id'], device['ip'], device['key'], device['name'])     
            case 'dj':
                if device['ip']:
                    return smart_ir(device['id'], device['ip'], device['key'], device['name'])
            case 'tv':
                if device['ip']:
                    return smart_tv(device['id'], device['ip'], device['key'], device['name'])
            case 'jtmspro':
                if device['ip']:
                    return smart_lock(device['id'], device['ip'], device['key'], device['name'])


DEVICES_FILE = "devices.json"
def load_devices():
    """Load devices from devices.json"""
    with open(DEVICES_FILE) as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get('devices', [])


def _build_device_objects(devices):
    """Build device objects concurrently to reduce startup time."""
    if not devices:
        return []

    max_workers = min(32, len(devices))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(devices_status, devices))


def organize_devices(device_list):
    
    devices = device_list
    
    _organized_list_of_rooms = []
    for index in range(len(devices)):
        tmp_name = devices[index]["name"]
        
        
        if "Q" in tmp_name:
            tmp_index_start = tmp_name.index("Q")
            tmp_index_end = tmp_index_start + 3
            tmp_room = tmp_name[tmp_index_start:tmp_index_end]
            
            if not tmp_room in _organized_list_of_rooms:
                _organized_list_of_rooms.append(tmp_room)
        else:
            continue
        
    _sorted_organized_list_of_rooms = {"Floors":[]}
    
    for _room in  _organized_list_of_rooms:
        _int_room = _room[1:len(_room)]
        _int_floor = int(_int_room[0:1])
        _int_room_number = int(_int_room[1:2])
        while len(_sorted_organized_list_of_rooms["Floors"]) <= _int_floor:
            _sorted_organized_list_of_rooms["Floors"].append([])
            
        while len(_sorted_organized_list_of_rooms["Floors"][_int_floor]) < _int_room_number:
            _sorted_organized_list_of_rooms["Floors"][_int_floor].append([])
            
        _sorted_organized_list_of_rooms["Floors"][_int_floor][_int_room_number-1] = {"Name": _room, "Devices": [], "Objects": []}

        
    

    _outside_devices = {"Devices": [], "Objects": []}
    device_objects = _build_device_objects(devices)

    for device_dict, device_obj in zip(devices, device_objects):
        tmp_name = device_dict["name"]
        if "Q" in tmp_name:
            tmp_index_start = tmp_name.index("Q")
            tmp_index_end = tmp_index_start + 3
            tmp_room = tmp_name[tmp_index_start:tmp_index_end]
            
            _int_room = tmp_room[1:len(tmp_room)]
            _int_floor = int(_int_room[0:1])
            _int_room_number = int(_int_room[1:2])
            
            _sorted_organized_list_of_rooms["Floors"][_int_floor][_int_room_number-1]["Devices"].append(device_dict)
            _sorted_organized_list_of_rooms["Floors"][_int_floor][_int_room_number-1]["Objects"].append(device_obj)
        else:
            _outside_devices["Devices"].append(device_dict)
            _outside_devices["Objects"].append(device_obj)
            
        
    return _sorted_organized_list_of_rooms, _outside_devices



if __name__ == "__main__":
    devices = load_devices()
    
    my_devices, my_outside_devices = organize_devices(devices)
    
        
    '''floor = int(input("indique o seu piso"))
    room = int(input("indique o seu quarto"))
    
    for device in my_devices["Floors"][floor][room]["Devices"]:
        status = "ONLINE" if device['ip'] else "OFFLINE"
        print(f"{device['name'][0:device['name'].index("Q")]}-->{status}")'''
    
    
       
            
   
    

    

