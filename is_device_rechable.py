import subprocess

def is_device_reachable(ip):
    if not ip:
        return False

    result = subprocess.run(
    ["ping", "-c", "1", "-W", "1", ip],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    check=False,
    )
    return result.returncode == 0
