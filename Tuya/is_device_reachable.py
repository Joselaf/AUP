import subprocess
import platform
import re


def is_device_reachable(ip):
    if not ip:
        return False

    if platform.system().lower() != "linux":
        raise RuntimeError("is_device_reachable is supported only on Linux")

    cmd = ["ping", "-c", "1", "-W", "1", ip]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=2,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def get_ip_mac(ip):
    if not ip:
        return None

    if platform.system().lower() != "linux":
        raise RuntimeError("get_ip_mac is supported only on Linux")

    cmd = ["ip", "neigh", "show", ip]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=2,
            text=True,
        )
        if result.returncode != 0 or not result.stdout:
            return None

        match = re.search(r"lladdr\s+([0-9a-fA-F:]{17})", result.stdout)
        if not match:
            return None

        return match.group(1).lower()
    except subprocess.TimeoutExpired:
        return None


def is_expected_mac(ip, expected_mac):
    if not ip or not expected_mac:
        return False

    current_mac = get_ip_mac(ip)
    if not current_mac:
        return False

    return current_mac == expected_mac.lower()
