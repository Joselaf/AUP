import subprocess
import platform


def is_device_reachable(ip):
    if not ip:
        return False
    else:
        cmd = ["ping", "-c", "1", ip]
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
