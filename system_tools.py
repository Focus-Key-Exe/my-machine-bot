
"""
System tools for the machine bot.
These functions gather information about your local machine.
"""

import psutil
import platform
import socket
import os
from datetime import datetime


def get_system_info() -> dict:
    """Get basic system information."""
    uname = platform.uname()
    return {
        "system": uname.system,
        "node_name": uname.node,
        "release": uname.release,
        "version": uname.version,
        "machine": uname.machine,
        "processor": uname.processor,
        "python_version": platform.python_version(),
    }


def get_cpu_info() -> dict:
    """Get CPU usage and information."""
    cpu_freq = psutil.cpu_freq()
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "max_frequency_mhz": round(cpu_freq.max, 2) if cpu_freq else "N/A",
        "current_frequency_mhz": round(cpu_freq.current, 2) if cpu_freq else "N/A",
        "cpu_usage_percent": psutil.cpu_percent(interval=1),
        "per_core_usage": psutil.cpu_percent(interval=1, percpu=True),
    }


def get_memory_info() -> dict:
    """Get RAM usage information."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total_gb": round(mem.total / (1024**3), 2),
        "available_gb": round(mem.available / (1024**3), 2),
        "used_gb": round(mem.used / (1024**3), 2),
        "usage_percent": mem.percent,
        "swap_total_gb": round(swap.total / (1024**3), 2),
        "swap_used_gb": round(swap.used / (1024**3), 2),
        "swap_percent": swap.percent,
    }


def get_disk_info() -> dict:
    """Get disk usage information."""
    partitions = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            partitions.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "filesystem": partition.fstype,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "usage_percent": usage.percent,
            })
        except PermissionError:
            continue
    return {"partitions": partitions}


def get_network_info() -> dict:
    """Get network interface information."""
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        local_ip = "Unable to resolve"
    
    interfaces = {}
    net_if_addrs = psutil.net_if_addrs()
    for interface_name, addresses in net_if_addrs.items():
        interfaces[interface_name] = []
        for addr in addresses:
            interfaces[interface_name].append({
                "address": addr.address,
                "family": str(addr.family),
            })
    
    net_io = psutil.net_io_counters()
    return {
        "hostname": hostname,
        "local_ip": local_ip,
        "interfaces": interfaces,
        "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
        "bytes_received_mb": round(net_io.bytes_recv / (1024**2), 2),
    }


def get_process_info(limit: int = 10) -> dict:
    """Get top processes by memory usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
        try:
            pinfo = proc.info
            processes.append({
                "pid": pinfo['pid'],
                "name": pinfo['name'],
                "memory_percent": round(pinfo['memory_percent'], 2) if pinfo['memory_percent'] else 0,
                "cpu_percent": round(pinfo['cpu_percent'], 2) if pinfo['cpu_percent'] else 0,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Sort by memory usage and return top N
    processes.sort(key=lambda x: x['memory_percent'], reverse=True)
    return {"top_processes_by_memory": processes[:limit]}


def get_battery_info() -> dict:
    """Get battery information (for laptops)."""
    battery = psutil.sensors_battery()
    if battery:
        return {
            "percent": battery.percent,
            "power_plugged": battery.power_plugged,
            "time_left_minutes": round(battery.secsleft / 60, 1) if battery.secsleft > 0 else "Charging/Full",
        }
    return {"status": "No battery detected (desktop or not available)"}


def get_uptime() -> dict:
    """Get system uptime."""
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    now = datetime.now()
    uptime = now - boot_time
    
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return {
        "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": f"{days}d {hours}h {minutes}m {seconds}s",
    }


# Tool registry for the chatbot
TOOLS = {
    "get_system_info": {
        "function": get_system_info,
        "description": "Get basic system information like OS, hostname, and processor",
    },
    "get_cpu_info": {
        "function": get_cpu_info,
        "description": "Get CPU usage, core count, and frequency information",
    },
    "get_memory_info": {
        "function": get_memory_info,
        "description": "Get RAM and swap memory usage",
    },
    "get_disk_info": {
        "function": get_disk_info,
        "description": "Get disk partition and storage usage information",
    },
    "get_network_info": {
        "function": get_network_info,
        "description": "Get network interfaces, IP addresses, and data transfer stats",
    },
    "get_process_info": {
        "function": get_process_info,
        "description": "Get top processes by memory usage",
    },
    "get_battery_info": {
        "function": get_battery_info,
        "description": "Get battery status and charge level (for laptops)",
    },
    "get_uptime": {
        "function": get_uptime,
        "description": "Get system boot time and uptime duration",
    },
}
