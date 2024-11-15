import time
from collections.abc import Callable, Iterable, Iterator, Sequence
from operator import itemgetter
from statistics import mean, median
from threading import Event, Thread
from types import TracebackType
from typing import overload

from typing_extensions import Self

from .measure.base import Assey, Measurer, MeasurerGroup

MIN_INTERVAL = 1e-6

Measurements = tuple[float | int, ...]


class Observation:
    def __init__(
        self,
        name: str,
        number: int,
        begin: float,
        end: float,
        keys: tuple[str, ...],
        times: list[float],
        values: list[Assey],
    ) -> None:
        if begin > end:
            msg = f"Begin must be less than end, got {begin=} and {end=}."
            raise ValueError(msg)
        if any(len(v) != len(keys) for v in values):
            max_len = max(len(v) for v in values)
            msg = f"values must have {len(keys)} elements, but there is a value with {max_len}."
            raise ValueError(msg)
        if len(times) != len(values):
            msg = "times and values must have the same length."
            raise ValueError(msg)
        self.name = name
        self.number = number
        self.begin = begin
        self.end = end
        self.keys = keys
        self.times = times
        self.values = values

    def apply(self, func: Callable[[Iterable[float | int]], float | int]) -> Assey:
        """Apply a function to each key"""
        return tuple(func(v) for v in zip(*self.values, strict=False))

    def mean(self) -> Assey:
        """Calculate the mean of the values"""
        return self.apply(mean)

    def median(self) -> Assey:
        """Calculate the median of the values"""
        return self.apply(median)

    def __getitem__(
        self,
        key: str | tuple[str, ...],
    ) -> Measurements | tuple[Measurements, ...]:
        """Get the values of a key"""
        if isinstance(key, str):
            key = (key,)
        keys = tuple(self.keys.index(k) for k in key)
        return tuple(map(itemgetter(*keys), self.values))


class ObservationSequence(Sequence[Observation]):
    def __init__(self, observations: Iterable[Observation]) -> None:
        self._observations = list(observations)

    @overload
    def __getitem__(self, index: int) -> Observation: ...

    @overload
    def __getitem__(self, index: slice) -> "ObservationSequence": ...

    def __getitem__(self, index: int | slice) -> "Observation | ObservationSequence":
        result = self._observations[index]
        if isinstance(result, Observation):
            return result
        return ObservationSequence(result)

    def __len__(self) -> int:
        return len(self._observations)

    def __iter__(self) -> Iterator[Observation]:
        return iter(self._observations)

    def aggregate(
        self,
        func: Callable[[Iterable[float | int]], float | int],
        name: str | None = None,
    ) -> Observation:
        """Aggregate the values of the observations"""
        return Observation(
            name=name or "aggregate",
            number=0,
            begin=self._observations[0].begin,
            end=self._observations[-1].end,
            keys=self._observations[0].keys,
            times=[(o.times[0] + o.times[-1]) / 2 for o in self._observations],
            values=[o.apply(func) for o in self._observations],
        )

    def means(self) -> Observation:
        """Calculate the means of the values"""
        return self.aggregate(mean, name="means")

    def medians(self) -> Observation:
        """Calculate the medians of the values"""
        return self.aggregate(median, name="medians")


def _now() -> float:
    # TODO(@rilshok): rebase to time.perf_counter()
    return time.time()


class Observer:
    def __init__(self, interval: float, *mesurers: Measurer) -> None:
        if interval < MIN_INTERVAL:
            msg = f"Interval must be greater than 0, got {interval=}."
            if 0.0 < interval < MIN_INTERVAL:
                msg += f" Consider using a value greater than {MIN_INTERVAL:.0e}."
            raise ValueError(msg)

        self._measurer = MeasurerGroup(mesurers)
        self._interval = interval

        self._thread: Thread | None = None
        self._pause_event = Event()
        self._stop_event = Event()

        self._current_event_name: str | None = None
        self._current_begin: float | None = None
        self._current_times: list[float] = []
        self._current_values: list[Assey] = []

        self._observations: list[Observation] = []

    @property
    def observations(self) -> ObservationSequence:
        """Get the observations"""
        return ObservationSequence(self._observations)

    def assay(self) -> Assey:
        """Take an assay of the current state"""
        return self._measurer.assey()

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
            keys=self._measurer.keys_full,
            times=self._current_times,
            values=self._current_values,
        )
        self._observations.append(observation)
        self._current_begin = None
        self._current_times = []
        self._current_values = []
        return observation

    def _observe(self) -> None:
        while not self._stop_event.is_set():
            self._pause_event.wait()  # Wait until not paused
            now1 = _now()
            assay = self.assay()
            now2 = _now()
            self._current_times.append((now1 + now2) / 2)
            self._current_values.append(assay)
            time.sleep(self._interval)

    def start(self, name: str | None = None) -> None:
        """Start monitoring"""
        if self._thread and self._thread.is_alive():
            self._flush()
        if name is not None:
            self._current_event_name = name
        self._current_begin = _now()
        self._pause_event.set()  # Ensure it's not paused
        self._stop_event.clear()
        self._thread = Thread(target=self._observe)
        self._thread.start()

    def stop(self) -> None:
        """Stop monitoring"""
        if not self._thread or not self._thread.is_alive():
            return
        self._stop_event.set()
        self._pause_event.set()  # Unpause to allow stopping
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
