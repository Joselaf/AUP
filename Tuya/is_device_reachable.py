import subprocess
import platform


def is_device_reachable(ip):
    if not ip:
        return False

    if platform.system().lower().startswith("win"):
        cmd = ["ping", "-n", "1", "-w", "1000", ip]
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
