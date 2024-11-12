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

    def __init__(self, interval: float, *, pid: int | None = None):
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


class VirtualMemoryObserver(Observer):
    """Virtual memory observer

    Measures the virtual memory usage of the system

    Investigated metrics:
        total (int): Total physical memory available
        available (int): The memory that can be given instantly to processes without the system going into swap
        percent (float): The percentage usage calculated as (total - available) / total * 100
        used (int): Memory used, calculated differently depending on the platform and designed for informational purposes only:
            macOS: active + wired
            BSD: active + wired + cached
            Linux: total - free
        free (int): Memory not being used at all (zeroed) that is readily available
    """

    def __init__(self, interval: float):
        keys = ("total", "available", "percent", "used", "free")
        super().__init__(keys=keys, interval=interval)

    def assay(self) -> tuple[int, int, float, int, int]:
        svmem = psutil.virtual_memory()
        return (
            svmem.total,
            svmem.available,
            svmem.percent,
            svmem.used,
            svmem.free,
        )


class SwapMemoryObserver(Observer):
    """Swap memory observer

    Measures the swap memory usage of the system

    Investigated metrics:
        total (int): The total swap memory in bytes
        used (int): The used swap memory in bytes
        free (int): The free swap memory in bytes
        percent (float): The percentage usage
        sin (int): No. of bytes the system has swapped in from disk (cumulative)
        sout (int): No. of bytes the system has swapped out from disk (cumulative)
    """

    def __init__(self, interval: float):
        keys = ("total", "used", "free", "percent", "sin", "sout")
        super().__init__(keys=keys, interval=interval)

    def assay(self) -> tuple[int, int, int, float, int, int]:
        sswap = psutil.swap_memory()
        return (
            sswap.total,
            sswap.used,
            sswap.free,
            sswap.percent,
            sswap.sin,
            sswap.sout,
        )


class ProcessMemoryObserver(Observer):
    """Process memory observer

    Measures the memory usage of a specific process

    Investigated metrics:
        rss (int): Amount of physical memory used by the process in RAM
        vms (int): Total amount of virtual memory allocated to the process
        uss (int): Memory unique to the process that would be freed if the process were terminated
    """

    def __init__(self, interval: float, *, pid: int | None = None):
        keys = ("rss", "vms", "uss")
        super().__init__(keys=keys, interval=interval)
        self._process = psutil.Process(pid)

    def assay(self) -> tuple[int, int, int]:
        pfullmem = self._process.memory_full_info()
        return (
            pfullmem.rss,
            pfullmem.vms,
            pfullmem.uss,
        )
