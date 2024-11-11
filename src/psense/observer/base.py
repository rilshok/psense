import time
from abc import ABC, abstractmethod

from typing_extensions import Self
from types import TracebackType
from threading import Thread

MIN_INTERVAL = 1e-6

Cortege = tuple[float, ...] | tuple[int, ...]
Assey = tuple[float | int | Cortege, ...]
Event = str | int


class Observation:
    def __init__(
        self,
        name: str,
        number: int,
        begin: float,
        end: float,
        keys: tuple[str, ...],
        values: list[Assey],
    ) -> None:
        if begin > end:
            msg = f"Begin must be less than end, got {begin=} and {end=}."
            raise ValueError(msg)
        if any(len(v) != len(keys) for v in values):
            max_len = max(len(v) for v in values)
            msg = f"values must have {len(keys)} elements, but there is a value with {max_len}."
            raise ValueError(msg)
        self.name = name
        self.number = number
        self.begin = begin
        self.end = end
        self.keys = keys
        self.values = values


class ObservationSet:
    def __init__(self, observations: list[Observation]) -> None:
        self._observations = observations


def _now() -> float:
    # TODO(@rilshok): rebase to time.perf_counter()
    return time.time()


class Observer(ABC):
    def __init__(self, keys: tuple[str, ...], interval: float) -> None:
        if interval < MIN_INTERVAL:
            msg = f"Interval must be greater than 0, got {interval=}."
            if 0.0 < interval < MIN_INTERVAL:
                msg += f" Consider using a value greater than {MIN_INTERVAL:.0e}."
            raise ValueError(msg)
        self._keys = keys
        self._interval = interval

        self._running = False
        self._thread: Thread | None = None

        self._current_event_name: str | None = None
        self._current_begin: float | None = None
        self._current_values: list[Assey] = []

        self._observations: list[Observation] = []

    @property
    def observations(self) -> list[Observation]:
        """The list of observations"""
        return self._observations.copy()

    @abstractmethod
    def assay(self) -> Assey:
        """Take an assay of the current state"""
        raise NotImplementedError()

    def _flush(self) -> Observation:
        if self._current_begin is None:
            msg = "Current begin is not set. "
            msg = f"No current event to flush. {msg}"
            raise RuntimeError(msg.strip())

        name = self._current_event_name or str(len(self._observations))

        observation = Observation(
            name=name,
            number=len(self._observations),
            begin=self._current_begin,
            end=_now(),
            keys=self._keys,
            values=self._current_values,
        )
        self._observations.append(observation)
        self._current_begin = None
        self._current_values = []
        return observation

    def _observe(self, interval: float) -> None:
        while self._running:
            self._current_values.append(self.assay())
            time.sleep(interval)

    def start(self, name: str | None = None) -> None:
        """Start monitoring"""
        if self._running:
            self._flush()
        if name is not None:
            self._current_event_name = name
        self._current_begin = _now()
        self._running = True
        self._thread = Thread(target=self._observe, args=(self._interval,))
        self._thread.start()

    def stop(self) -> None:
        """Stop monitoring"""
        if not self._running:
            return
        self._running = False
        if self._thread:
            self._thread.join()
        self._flush()

    def __call__(self, name: str) -> Self:
        """Rename the current event"""
        self._current_event_name = name
        return self

    def __enter__(self) -> Self:
        """Take an initial assay and start monitoring if interval is set"""
        self.start()
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,  # noqa: F841
        value: BaseException | None,  # noqa: F841
        traceback: TracebackType | None,  # noqa: F841
    ) -> None:
        """Stop monitoring and take a final assay when exiting the context manager"""
        self.stop()
