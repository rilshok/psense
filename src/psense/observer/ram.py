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
