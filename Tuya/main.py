import json
import sys
import os
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from devices import *
from is_device_reachable import is_device_reachable, is_expected_mac
    

def devices_status(device):
    ip = device['ip']
    expected_mac = device['mac']
    category = device.get('category')

    # Devices without a local IP (e.g. BLE/Zigbee locks) — skip network checks
    if not ip:
        match category:
            case 'ms':
                return Lock(device['id'], device['key'], device['name'], device['version'])
            case 'jtmspro':
                return Smart_lock(device['id'], device['key'], device['name'], device['version'])
        return None

    if not is_device_reachable(ip):
        return None

    # TinyTuya wizard data can become stale; reject IPs now owned by another host.
    if expected_mac and not is_expected_mac(ip, expected_mac):
        return None

    else:
        if device['ip']:     
            match category:
                case 'dlq' if ("consumo" in device['name'].lower()):
                        return Consumption_breaker(device['id'],device['ip'],device['key'],device['name'],device['version'])
                case 'dlq':
                        return Breaker(device['id'], device['ip'], device['key'], device['name'],device['version'])
                case 'kg':
                        return Breaker(device['id'], device['ip'], device['key'], device['name'],device['version'])
                case 'tdp':
                        return Heater(device['id'], device['ip'], device['key'], device['name'],device['version'])
                case 'mcs':
                        return Contact_sensor(device['id'], device['ip'], device['key'], device['name'],device['version'])  
                case 'hps':
                        return Presence_sensor(device['id'], device['ip'], device['key'], device['name'],device['version'])
                case 'cz':
                        return Smart_plug(device['id'], device['ip'], device['key'], device['name'],device['version'])
                case 'dj'if("\u6b27\u7248A60-WB 9W RGBCW 220V E27" in device['name'].upper()):
                        return Smart_bulb(device['id'], device['ip'], device['key'], device['name'],device['version'])
                case 'dj'if("esmax" in device['name'].lower()):
                        return Esmax(device['id'], device['ip'], device['key'], device['name'],device['version'])     
                case 'dj':
                        return Smart_ir(device['id'], device['ip'], device['key'], device['name'],device['version'])
                case 'tv':
                        return Smart_tv(device['id'], device['ip'], device['key'], device['name'],device['version'])
        else:
            return None


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


def organize_structure(device_list):
    """Build floor/room structure from device names only — no network scanning."""
    devices = device_list

    _organized_list_of_rooms = []
    for index in range(len(devices)):
        tmp_name = devices[index]["name"]
        if "Q" in tmp_name:
            tmp_index_start = tmp_name.index("Q")
            tmp_index_end = tmp_index_start + 3
            tmp_room = tmp_name[tmp_index_start:tmp_index_end]
            if tmp_room not in _organized_list_of_rooms:
                _organized_list_of_rooms.append(tmp_room)

    _sorted_organized_list_of_rooms = {"Floors": []}
    for _room in _organized_list_of_rooms:
        _int_room = _room[1:]
        _int_floor = int(_int_room[0])
        _int_room_number = int(_int_room[1])
        while len(_sorted_organized_list_of_rooms["Floors"]) <= _int_floor:
            _sorted_organized_list_of_rooms["Floors"].append([])
        while len(_sorted_organized_list_of_rooms["Floors"][_int_floor]) < _int_room_number:
            _sorted_organized_list_of_rooms["Floors"][_int_floor].append([])
        _sorted_organized_list_of_rooms["Floors"][_int_floor][_int_room_number - 1] = {
            "Name": _room, "Devices": [], "Objects": []
        }

    _outside_devices = {"Devices": [], "Objects": []}
    for device_dict in devices:
        tmp_name = device_dict["name"]
        if "Q" in tmp_name:
            tmp_index_start = tmp_name.index("Q")
            tmp_index_end = tmp_index_start + 3
            tmp_room = tmp_name[tmp_index_start:tmp_index_end]
            _int_room = tmp_room[1:]
            _int_floor = int(_int_room[0])
            _int_room_number = int(_int_room[1])
            _sorted_organized_list_of_rooms["Floors"][_int_floor][_int_room_number - 1]["Devices"].append(device_dict)
            _sorted_organized_list_of_rooms["Floors"][_int_floor][_int_room_number - 1]["Objects"].append(None)
        else:
            _outside_devices["Devices"].append(device_dict)
            _outside_devices["Objects"].append(None)

    return _sorted_organized_list_of_rooms, _outside_devices

    
    
       
            
   
    

    

