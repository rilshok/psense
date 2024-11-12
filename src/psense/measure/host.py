import psutil

from .base import Measurer


class CPUMeasurer(Measurer):
    """CPU usage measurer

    Measures the CPU usage of the system and each core

    Investigated metrics:
        total (float): Total percentage of CPU used
        user: (float): System-wide CPU user time
        system: (float): System-wide CPU system time
        idle: (float): System-wide CPU idle

    """

    def __init__(self) -> None:
        super().__init__(
            name="CPU",
            keys=("total", "user", "system", "idle"),
        )

    def assey(self) -> tuple[float, float, float, float]:
        total_usage = psutil.cpu_percent()
        cpu_times = psutil.cpu_times()

        return (
            total_usage,
            cpu_times.user,
            cpu_times.system,
            cpu_times.idle,
        )


class ProcessCPUMeasurer(Measurer):
    """Process CPU usage measurer

    Measures the CPU usage of a specific process

    Investigated metrics:
        percent (float): Percentage of CPU used by the process
        user (float): System-wide CPU user time
        system (float): System-wide CPU system time

    """

    def __init__(self, pid: int | None = None) -> None:
        self._process = psutil.Process(pid)
        super().__init__(
            name=f"CPU[{self._process.pid}]",
            keys=("percent", "user", "system"),
        )

    def assey(self) -> tuple[float, float, float]:
        cpu_percent = self._process.cpu_percent(interval=None)
        cpu_times = self._process.cpu_times()
        return (
            cpu_percent,
            cpu_times.user,
            cpu_times.system,
        )


class MemMeasurer(Measurer):
    """Virtual memory measurer

    Measures the virtual memory usage of the system

    Investigated metrics:
        total (int): Total physical memory available
        available (int): The memory that can be given instantly
                         to processes without the system going into swap
        percent (float): The percentage usage calculated as (total - available) / total * 100
        used (int): Memory used, calculated differently depending on the platform
                    and designed for informational purposes only:
                        macOS: active + wired
                        BSD: active + wired + cached
                        Linux: total - free
        free (int): Memory not being used at all (zeroed) that is readily available
    """

    def __init__(self) -> None:
        super().__init__(name="MEM", keys=("total", "available", "percent", "used", "free"))

    def assey(self) -> tuple[int, int, float, int, int]:
        svmem = psutil.virtual_memory()
        return (
            svmem.total,
            svmem.available,
            svmem.percent,
            svmem.used,
            svmem.free,
        )


class SwapMeasurer(Measurer):
    """Swap memory measurer

    Measures the swap memory usage of the system

    Investigated metrics:
        total (int): The total swap memory in bytes
        used (int): The used swap memory in bytes
        free (int): The free swap memory in bytes
        percent (float): The percentage usage
        sin (int): No. of bytes the system has swapped in from disk (cumulative)
        sout (int): No. of bytes the system has swapped out from disk (cumulative)
    """

    def __init__(self) -> None:
        super().__init__(
            name="SWP",
            keys=("total", "used", "free", "percent", "sin", "sout"),
        )

    def assey(self) -> tuple[int, int, int, float, int, int]:
        sswap = psutil.swap_memory()
        return (
            sswap.total,
            sswap.used,
            sswap.free,
            sswap.percent,
            sswap.sin,
            sswap.sout,
        )


class ProcessMemMeasurer(Measurer):
    """Process memory measurer

    Measures the memory usage of a specific process

    Investigated metrics:
        rss (int): Amount of physical memory used by the process in RAM
        vms (int): Total amount of virtual memory allocated to the process
        uss (int): Memory unique to the process that would be freed if the process were terminated
    """

    def __init__(self, pid: int | None = None) -> None:
        self._process = psutil.Process(pid)
        super().__init__(
            name=f"MEM[{self._process.pid}]",
            keys=("rss", "vms", "uss"),
        )

    def assey(self) -> tuple[int, int, int]:
        pfullmem = self._process.memory_full_info()
        return (
            pfullmem.rss,
            pfullmem.vms,
            pfullmem.uss,
        )
