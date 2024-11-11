import psutil


from .base import Observer


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

    def __init__(self, interval: float, pid: int | None = None):
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
