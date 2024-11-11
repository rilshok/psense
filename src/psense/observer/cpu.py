import psutil
from .base import Observer
import attr


@attr.s(slots=True, kw_only=True)
class CPUUsage:
    # Percentage of CPU used by each core
    per_core: list[float] = attr.ib(factory=list)

    # Total percentage of CPU used
    total: float = attr.ib()

    # System-wide CPU times
    user: float = attr.ib()
    system: float = attr.ib()
    idle: float = attr.ib()


class CPUUsageObserver(Observer[CPUUsage]):
    def assay(self) -> CPUUsage:
        per_core_usage = psutil.cpu_percent(percpu=True)
        total_usage = psutil.cpu_percent()
        cpu_times = psutil.cpu_times()

        return CPUUsage(
            per_core=per_core_usage,
            total=total_usage,
            user=cpu_times.user,
            system=cpu_times.system,
            idle=cpu_times.idle,
        )


@attr.s(slots=True, kw_only=True)
class ProcessCPUUsage:
    # Percentage of CPU used by the process
    percent: float = attr.ib()

    # System-wide CPU times used by the process
    user: float = attr.ib()
    system: float = attr.ib()


class ProcessCPUUsageObserver(Observer[ProcessCPUUsage]):
    def __init__(self, interval: float | None = None, pid: int | None = None):
        super().__init__()
        self._interval = interval
        self._process = psutil.Process(pid)

    def assay(self) -> ProcessCPUUsage:
        cpu_percent = self._process.cpu_percent(interval=self._interval)
        cpu_times = self._process.cpu_times()

        return ProcessCPUUsage(
            percent=cpu_percent,
            user=cpu_times.user,
            system=cpu_times.system,
        )
