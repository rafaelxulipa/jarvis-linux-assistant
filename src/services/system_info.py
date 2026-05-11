from __future__ import annotations
import os
import platform
import socket
import subprocess
import psutil
from datetime import datetime, timedelta


def get_cpu_percent() -> float:
    return psutil.cpu_percent(interval=None)


def get_ram_info() -> dict:
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024 ** 3), 1),
        "used_gb":  round(mem.used  / (1024 ** 3), 1),
        "percent":  mem.percent,
    }


def get_disk_info(path: str = "/") -> dict:
    disk = psutil.disk_usage(path)
    return {
        "total_gb": round(disk.total / (1024 ** 3), 1),
        "used_gb":  round(disk.used  / (1024 ** 3), 1),
        "percent":  disk.percent,
    }


def get_uptime() -> str:
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes = remainder // 60
    return f"{hours:02d}h {minutes:02d}m"


def get_hostname() -> str:
    return socket.gethostname()


def get_ip_address() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "N/A"


def get_internet_status() -> bool:
    try:
        socket.setdefaulttimeout(2)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except Exception:
        return False


def get_cpu_temperature() -> float | None:
    try:
        temps = psutil.sensors_temperatures()
        for key in ("coretemp", "cpu_thermal", "k10temp", "acpitz"):
            if key in temps:
                entries = temps[key]
                if entries:
                    return entries[0].current
    except Exception:
        pass
    # fallback: read directly
    try:
        thermal_path = "/sys/class/thermal/thermal_zone0/temp"
        with open(thermal_path) as f:
            return float(f.read().strip()) / 1000.0
    except Exception:
        return None


def get_os_info() -> dict:
    return {
        "system":  platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "distro":  _get_distro(),
    }


def _get_distro() -> str:
    try:
        import distro
        return f"{distro.name()} {distro.version()}"
    except ImportError:
        pass
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return platform.system()


def get_network_io() -> dict:
    net = psutil.net_io_counters()
    return {
        "bytes_sent": net.bytes_sent,
        "bytes_recv": net.bytes_recv,
    }


def get_process_count() -> int:
    return len(list(psutil.process_iter()))


def get_battery_info() -> dict | None:
    try:
        bat = psutil.sensors_battery()
        if bat is None:
            return None
        return {
            "percent":  round(bat.percent, 1),
            "plugged":  bat.power_plugged,
        }
    except Exception:
        return None


def snapshot() -> dict:
    """Full system snapshot for dashboard."""
    return {
        "cpu":        get_cpu_percent(),
        "ram":        get_ram_info(),
        "disk":       get_disk_info(),
        "uptime":     get_uptime(),
        "hostname":   get_hostname(),
        "ip":         get_ip_address(),
        "internet":   get_internet_status(),
        "temp":       get_cpu_temperature(),
        "os":         get_os_info(),
        "processes":  get_process_count(),
        "battery":    get_battery_info(),
        "timestamp":  datetime.now().isoformat(),
    }
