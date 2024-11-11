import psutil
from .base import Observer


class CPUUsageObserver(Observer):
    """CPU usage observer

    Measures the CPU usage of the system and each core

    Investigated metrics:
        per_core (tuple[float]): Percentage of CPU used by each core
        total (float): Total percentage of CPU used
        user: (float): System-wide CPU user time
        system: (float): System-wide CPU system time
        idle: (float): System-wide CPU idle

    """

    def __init__(self, interval: float):
        keys = ("per_core", "total", "user", "system", "idle")
        super().__init__(keys=keys, interval=interval)

    def assay(self) -> tuple[tuple[float, ...], float, float, float, float]:
        per_core_usage = psutil.cpu_percent(percpu=True)
        total_usage = psutil.cpu_percent()
        cpu_times = psutil.cpu_times()

        return (
            tuple(per_core_usage),
            total_usage,
            cpu_times.user,
            cpu_times.system,
            cpu_times.idle,
        )


class ProcessCPUUsageObserver(Observer):
    """Process CPU usage observer

    Measures the CPU usage of a specific process

    Investigated metrics:
        percent (float): Percentage of CPU used by the process
        user (float): System-wide CPU user time
        system (float): System-wide CPU system time

    """

    def __init__(self, interval: float, pid: int | None = None):
        keys = ("percent", "user", "system")
        super().__init__(keys=keys, interval=interval)
        self._process = psutil.Process(pid)

    def assay(self) -> tuple[float, float, float]:
        cpu_percent = self._process.cpu_percent(interval=None)
        cpu_times = self._process.cpu_times()

        return (
            cpu_percent,
            cpu_times.user,
            cpu_times.system,
        )
