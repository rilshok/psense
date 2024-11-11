import psutil

from .base import Observer
import attr


@attr.s(slots=True, kw_only=True)
class SystemVirtualMemory:
    # total physical memory available
    total: int = attr.ib(type=int)

    # the memory that can be given instantly to processes without the
    # system going into swap
    available: int = attr.ib(type=int)

    # the percentage usage calculated as (total - available) / total * 100
    percent: float = attr.ib(type=float)

    # memory used, calculated differently depending on the platform and
    # designed for informational purposes only:
    # macOS: active + wired
    # BSD: active + wired + cached
    # Linux: total - free
    used: int = attr.ib(type=int)

    # memory not being used at all (zeroed) that is readily available
    free: int = attr.ib(type=int)


class VirtualMemoryObserver(Observer[SystemVirtualMemory]):
    def assay(self) -> SystemVirtualMemory:
        svmem = psutil.virtual_memory()
        return SystemVirtualMemory(
            total=svmem.total,
            available=svmem.available,
            percent=svmem.percent,
            used=svmem.used,
            free=svmem.free,
        )


@attr.s(slots=True, kw_only=True)
class SwapMemory:
    # the total swap memory in bytes
    total: int = attr.ib(type=int)

    # the used swap memory in bytes
    used: int = attr.ib(type=int)

    # the free swap memory in bytes
    free: int = attr.ib(type=int)

    # the percentage usage
    percent: float = attr.ib(type=float)

    # no. of bytes the system has swapped in from disk (cumulative)
    sin: int = attr.ib(type=int)

    # no. of bytes the system has swapped out from disk (cumulative)
    sout: int = attr.ib(type=int)


class SwapMemoryObserver(Observer[SwapMemory]):
    def assay(self) -> SwapMemory:
        sswap = psutil.swap_memory()
        return SwapMemory(
            total=sswap.total,
            used=sswap.used,
            free=sswap.free,
            percent=sswap.percent,
            sin=sswap.sin,
            sout=sswap.sout,
        )


@attr.s(slots=True, kw_only=True)
class ProcessMemory:
    # amount of physical memory used by the process in RAM
    rss: int = attr.ib(type=int)

    # total amount of virtual memory allocated to the process
    vms: int = attr.ib(type=int)

    # memory unique to the process that would be freed if the process were terminated
    uss: int = attr.ib(type=int)


class ProcessMemoryObserver(Observer[ProcessMemory]):
    def __init__(self, pid: int | None = None):
        super().__init__()
        self._process = psutil.Process(pid)

    def assay(self) -> ProcessMemory:
        pfullmem = self._process.memory_full_info()
        return ProcessMemory(
            rss=pfullmem.rss,
            vms=pfullmem.vms,
            uss=pfullmem.uss,
        )
