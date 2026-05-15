import json
import sys
import os
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from devices import *
from is_device_reachable import is_device_reachable, is_expected_mac

DEVICES_FILE = "devices.json"

# ---------------------------------------------------------------------------
# Device instantiation
# ---------------------------------------------------------------------------

def devices_status(device):
    ip = device["ip"]
    expected_mac = device["mac"]
    category = device.get("category")

    # BLE/Zigbee devices — no local IP, use cloud
    if not ip:
        match category:
            case "ms":
                return Lock(device["id"], device["key"], device["name"], device["version"])
            case "jtmspro":
                return Smart_lock(device["id"], device["key"], device["name"], device["version"])
        return None

    if not is_device_reachable(ip):
        return None

    if expected_mac and not is_expected_mac(ip, expected_mac):
        return None

    name_lower = device["name"].lower()
    match category:
        case "dlq" if "consumo" in name_lower:
            return Consumption_breaker(device["id"], ip, device["key"], device["name"], device["version"])
        case "dlq" | "kg":
            return Breaker(device["id"], ip, device["key"], device["name"], device["version"])
        case "tdp":
            return Heater(device["id"], ip, device["key"], device["name"], device["version"])
        case "mcs":
            return Contact_sensor(device["id"], ip, device["key"], device["name"], device["version"])
        case "hps":
            return Presence_sensor(device["id"], ip, device["key"], device["name"], device["version"])
        case "cz":
            return Smart_plug(device["id"], ip, device["key"], device["name"], device["version"])
        case "dj" if "\u6b27\u7248A60-WB 9W RGBCW 220V E27" in device["name"].upper():
            return Smart_bulb(device["id"], ip, device["key"], device["name"], device["version"])
        case "dj" if "esmax" in name_lower:
            return Esmax(device["id"], ip, device["key"], device["name"], device["version"])
        case "dj":
            return Smart_ir(device["id"], ip, device["key"], device["name"], device["version"])
        case "tv":
            return Smart_tv(device["id"], ip, device["key"], device["name"], device["version"])
    return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_devices():
    """Load devices from devices.json."""
    with open(DEVICES_FILE) as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get("devices", [])


def _parse_room_tag(name: str):
    """Return (floor, room_number) ints from a device name, or None if not a room device."""
    if "Q" not in name:
        return None
    idx = name.index("Q")
    tag = name[idx + 1: idx + 3]   # e.g. "11", "21"
    if len(tag) < 2 or not tag.isdigit():
        return None
    return int(tag[0]), int(tag[1])


def _build_floor_structure(devices: list) -> dict:
    """Build the empty Floors scaffold from device names (no network I/O)."""
    seen = set()
    structure = {"Floors": []}

    for device in devices:
        parsed = _parse_room_tag(device["name"])
        if parsed is None or parsed in seen:
            continue
        seen.add(parsed)
        floor, room_num = parsed

        while len(structure["Floors"]) <= floor:
            structure["Floors"].append([])
        while len(structure["Floors"][floor]) < room_num:
            structure["Floors"][floor].append([])

        structure["Floors"][floor][room_num - 1] = {
            "Name": f"Q{floor}{room_num}",
            "Devices": [],
            "Objects": [],
        }

    return structure


def _build_device_objects(devices: list) -> list:
    """Instantiate device objects concurrently to reduce startup time."""
    if not devices:
        return []
    with ThreadPoolExecutor(max_workers=min(32, len(devices))) as executor:
        return list(executor.map(devices_status, devices))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def organize_devices(device_list: list):
    """Build floor/room structure and instantiate all device objects (network I/O)."""
    structure = _build_floor_structure(device_list)
    outside = {"Devices": [], "Objects": []}
    device_objects = _build_device_objects(device_list)

    for device_dict, device_obj in zip(device_list, device_objects):
        parsed = _parse_room_tag(device_dict["name"])
        if parsed:
            floor, room_num = parsed
            structure["Floors"][floor][room_num - 1]["Devices"].append(device_dict)
            structure["Floors"][floor][room_num - 1]["Objects"].append(device_obj)
        else:
            outside["Devices"].append(device_dict)
            outside["Objects"].append(device_obj)

    return structure, outside


def organize_structure(device_list: list):
    """Build floor/room structure from device names only — no network scanning."""
    structure = _build_floor_structure(device_list)
    outside = {"Devices": [], "Objects": []}

    for device_dict in device_list:
        parsed = _parse_room_tag(device_dict["name"])
        if parsed:
            floor, room_num = parsed
            structure["Floors"][floor][room_num - 1]["Devices"].append(device_dict)
            structure["Floors"][floor][room_num - 1]["Objects"].append(None)
        else:
            outside["Devices"].append(device_dict)
            outside["Objects"].append(None)

    return structure, outside
