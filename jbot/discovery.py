"""Read-only device discovery. No commands are run against discovered devices."""
import json
import platform
import shutil
import subprocess

def _run(command: list[str], timeout: int = 8):
    try:
        return subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False, shell=False)
    except (OSError, subprocess.TimeoutExpired):
        return None

def discover_android() -> list[dict]:
    adb = shutil.which("adb")
    if not adb:
        return [{"kind": "android", "status": "unavailable", "detail": "ADB is not installed or not on PATH"}]
    result = _run([adb, "devices", "-l"])
    if result is None:
        return [{"kind": "android", "status": "error", "detail": "ADB discovery timed out or could not start"}]
    devices = []
    for line in result.stdout.splitlines()[1:]:
        line = line.strip()
        if not line or line.startswith("*"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            devices.append({"kind": "android", "serial": parts[0], "status": parts[1],
                            "details": parts[2:], "read_only": True})
    return devices or [{"kind": "android", "status": "none_detected", "detail": "ADB is installed, but no Android device was listed"}]

def discover_windows_pnp() -> list[dict]:
    if platform.system() != "Windows":
        return []
    script = "Get-PnpDevice -PresentOnly | Select-Object -Property Class,FriendlyName,Status,InstanceId | ConvertTo-Json -Compress"
    result = _run(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "AllSigned", "-Command", script], 12)
    if result is None or result.returncode != 0 or not result.stdout.strip():
        return [{"kind": "windows_pnp", "status": "unavailable", "detail": "Windows PnP query failed or was blocked by system policy"}]
    try:
        raw = json.loads(result.stdout)
    except json.JSONDecodeError:
        return [{"kind": "windows_pnp", "status": "error", "detail": "PnP response could not be parsed"}]
    if isinstance(raw, dict):
        raw = [raw]
    return [{"kind": "windows_pnp", "class": item.get("Class"), "name": item.get("FriendlyName"),
             "status": item.get("Status"), "instance_id": item.get("InstanceId"), "read_only": True}
            for item in raw if isinstance(item, dict)]

def discover() -> list[dict]:
    devices = discover_windows_pnp() + discover_android()
    if platform.system() == "Linux":
        devices.append({"kind": "linux_usb", "status": "not_implemented",
                        "detail": "Linux USB sysfs adapter is not yet implemented"})
    return devices
