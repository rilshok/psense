from nvitop import Device

from .base import Observer


def _as_device(device: int | Device) -> Device:
    if isinstance(device, int):
        return Device(device)
    return device


class GPUUtilObserver(Observer):
    def __init__(self, interval: float, *, device: int | Device):
        keys = ("percent", "temp", "fan")
        super().__init__(keys=keys, interval=interval)
        self._device = _as_device(device)

    def assay(self) -> tuple[int, int, int]:
        return (
            p if isinstance((p := self._device.gpu_utilization()), int) else -1,
            t if isinstance((t := self._device.temperature()), int) else -1,
            f if isinstance((f := self._device.fan_speed()), int) else -1,
        )


class GPUMemObserver(Observer):
    def __init__(self, interval: float, *, device: int | Device):
        keys = ("total", "available", "percent", "used")
        super().__init__(keys=keys, interval=interval)
        self._device = _as_device(device)

    def assay(self) -> tuple[int, int, int, int]:
        return (
            t if isinstance((t := self._device.total_memory()), int) else -1,
            a if isinstance((a := self._device.memory_free()), int) else -1,
            p if isinstance((p := self._device.memory_percent()), int) else -1,
            u if isinstance((u := self._device.memory_used()), int) else -1,
        )


class AllGPUUtilObserver(Observer):
    def __init__(self, interval: float):
        keys = ("percent", "temp", "fan")
        super().__init__(keys=keys, interval=interval)
        self._devices = Device.all()

    def _get_percent(self) -> tuple[int, ...]:
        return tuple(
            p if isinstance((p := device.gpu_utilization()), int) else -1
            for device in self._devices
        )

    def _get_gpu_temp(self) -> tuple[int, ...]:
        return tuple(
            t if isinstance((t := device.temperature()), int) else -1 for device in self._devices
        )

    def _get_fan_speed(self) -> tuple[int, ...]:
        return tuple(
            f if isinstance((f := device.fan_speed()), int) else -1 for device in self._devices
        )

    def assay(self) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
        return (
            self._get_percent(),
            self._get_gpu_temp(),
            self._get_fan_speed(),
        )


class AllGpuMemObserver(Observer):
    def __init__(self, interval: float):
        keys = ("total", "available", "percent", "used")
        super().__init__(keys=keys, interval=interval)
        self._devices = Device.all()

    def _get_total(self) -> tuple[int, ...]:
        return tuple(
            t if isinstance((t := device.total_memory()), int) else -1 for device in self._devices
        )

    def _get_available(self) -> tuple[int, ...]:
        return tuple(
            a if isinstance((a := device.memory_free()), int) else -1 for device in self._devices
        )

    def _get_percent(self) -> tuple[int, ...]:
        return tuple(
            p if isinstance((p := device.memory_percent()), int) else -1 for device in self._devices
        )

    def _get_used(self) -> tuple[int, ...]:
        return tuple(
            u if isinstance((u := device.memory_used()), int) else -1 for device in self._devices
        )

    def assay(self) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
        return (
            self._get_total(),
            self._get_available(),
            self._get_percent(),
            self._get_used(),
        )
