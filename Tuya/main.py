import json
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import datetime

# Ensure the Tuya directory is on the path regardless of where script is run from
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tinytuya
from devices import{
    breaker,
    consumption_breaker,
    contact_sensor,
    esmax,
    heater,
    lock,
    presence_sensor,
    smart_bulb,
    smart_ir,
    smart_lock,
    smart_plug,
    smart_tv
}

DEVICES_FILE = "devices.json"

def load_devices():
    """Load devices from devices.json"""
    with open(DEVICES_FILE) as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get('devices', [])


def organize_devices(device_list):
    
    devices = device_list

    #print(devices[0])

    _organized_list = []
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
    _rooms_template = {"Rooms": []}
    
    for _room in  _organized_list_of_rooms:
        _int_room = _room[1:len(_room)]
        _int_floor = int(_int_room[0:1])
        _int_room_number = int(_int_room[1:2])
        while len(_sorted_organized_list_of_rooms["Floors"]) <= _int_floor:
            _sorted_organized_list_of_rooms["Floors"].append([])
            
        while len(_sorted_organized_list_of_rooms["Floors"][_int_floor]) < _int_room_number:
            _sorted_organized_list_of_rooms["Floors"][_int_floor].append([])
            
        _sorted_organized_list_of_rooms["Floors"][_int_floor][_int_room_number-1] = {"Name": _room, "Devices": []}

    index = 0
    for floor in _sorted_organized_list_of_rooms["Floors"]:
        index+=1
        
        
    

    _sorted_organized_list_of_rooms["Floors"][0][0]["Devices"]
    _outside_devices = []


    for device in devices:
        tmp_name = device["name"]
        
        if "Q" in tmp_name:
            tmp_index_start = tmp_name.index("Q")
            tmp_index_end = tmp_index_start + 3
            tmp_room = tmp_name[tmp_index_start:tmp_index_end]
            
            _int_room = tmp_room[1:len(tmp_room)]
            _int_floor = int(_int_room[0:1])
            _int_room_number = int(_int_room[1:2])
            
            _sorted_organized_list_of_rooms["Floors"][_int_floor][_int_room_number-1]["Devices"].append(device)
        else:
            _outside_devices.append(device)
        



    return _sorted_organized_list_of_rooms, _outside_devices

def devices_status(d):
    category = d['category']
    match category:
        case 'dlq'if("consumo" in device['name'].lower()):
            if not d['ip']:
                return None
            else:      
                d = consumption_breaker(device['id'], device['ip'], device['key'], device['name'])
                return d.get_status()

        case 'dlq':
            if(not d['ip']):
                return None
            else:
                d = breaker(device['id'], device['ip'], device['key'], device['name'])
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
            else:
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
    
    my_devices, my_outside_devices = organize_devices(devices)
    
      
    index_floor = 0
    index_room = 0
    for floor in my_devices["Floors"]:
        print(f"FLOOR:{index_floor}")
        index_floor+=1
        for room in floor:
            print(f"Room:{index_room}")
            index_room+=1
            for device in room["Devices"]:
                status = f"{datetime.now()}ONLINE" if device['ip'] else "OFFLINE"
                print(f"{device['name']}-->{status}")
                
        for device in my_outside_devices:
            status = "ONLINE" if device['ip'] else "OFFLINE"
            print(f"{device['name']}-->{status}")
        
    '''floor = int(input("indique o seu piso"))
    room = int(input("indique o seu quarto"))
    
    for device in my_devices["Floors"][floor][room]["Devices"]:
        status = "ONLINE" if device['ip'] else "OFFLINE"
        print(f"{device['name'][0:device['name'].index("Q")]}-->{status}")'''
    
    
       
            
   
    

    

