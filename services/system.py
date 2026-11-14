from dataclasses import dataclass

import psutil


@dataclass(frozen=True)
class Metric:
    percent: float
    used: float
    total: float


def get_cpu() -> Metric:
    percent = psutil.cpu_percent(interval=None)
    count = psutil.cpu_count(logical=True) or 1
    return Metric(percent=percent, used=percent, total=100.0)


def get_memory() -> Metric:
    vm = psutil.virtual_memory()
    return Metric(percent=vm.percent, used=vm.used, total=vm.total)


def get_disk() -> Metric:
    du = psutil.disk_usage("/")
    percent = du.used / du.total * 100
    return Metric(percent=percent, used=du.used, total=du.total)


def human_size(num_bytes: float) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(num_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"
