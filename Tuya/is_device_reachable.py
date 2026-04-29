import subprocess
import re
import socket


def is_device_reachable(ip, timeout=0.5):
    if not ip:
        return False
    try:
        # Tuya devices communicate on port 6668
        with socket.create_connection((ip, 6668), timeout=timeout):
            return True
    except (socket.timeout, OSError):
        return False


def get_ip_mac(ip):
    if not ip:
        return None
    else:
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
