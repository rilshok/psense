from nvitop import Device

from .base import Measurer, MeasurerGroup


def _as_device(device: int | Device) -> Device:
    if isinstance(device, int):
        return Device(device)
    return device


def _gpu_device_name(device: Device) -> str:
    name = device.name().replace("NVIDIA", "").strip()
    return f"GPU{device.index}({name})"


class NvGPUUtilMeasurer(Measurer):
    def __init__(self, device: int | Device = 0) -> None:
        self._device = _as_device(device)
        super().__init__(
            name=_gpu_device_name(self._device),
            keys=("percent", "temp", "fan"),
        )

    def assey(self) -> tuple[int, int, int]:
        return (
            p if isinstance((p := self._device.gpu_utilization()), int) else -1,
            t if isinstance((t := self._device.temperature()), int) else -1,
            f if isinstance((f := self._device.fan_speed()), int) else -1,
        )


class NvGPUMemMeasurer(Measurer):
    def __init__(self, device: int | Device = 0) -> None:
        self._device = _as_device(device)
        super().__init__(
            name=_gpu_device_name(self._device),
            keys=("total", "available", "percent", "used"),
        )

    def assey(self) -> tuple[int, int, int, int]:
        return (
            t if isinstance((t := self._device.total_memory()), int) else -1,
            a if isinstance((a := self._device.memory_free()), int) else -1,
            p if isinstance((p := self._device.memory_percent()), int) else -1,
            u if isinstance((u := self._device.memory_used()), int) else -1,
        )


class NvAllGPUUtilMeasurer(MeasurerGroup):
    def __init__(self) -> None:
        super().__init__(NvGPUUtilMeasurer(device) for device in Device.all())


class NvAllGpuMemMeasurer(MeasurerGroup):
    def __init__(self) -> None:
        super().__init__(NvGPUMemMeasurer(device) for device in Device.all())
