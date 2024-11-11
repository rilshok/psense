import time
from abc import ABC, abstractmethod

from typing_extensions import Self
from types import TracebackType
from threading import Thread

Сortege = tuple[float, ...] | tuple[int, ...]
Assey = tuple[float | int | Сortege, ...]


class Observer(ABC):
    def __init__(self, keys: tuple[str, ...], interval: float | None = None) -> None:
        self._keys = keys
        self._interval = interval
        self._running = False
        self._thread: Thread | None = None
        self._during: list[list[Assey]] = []

    @property
    def during(self) -> list[list[Assey]]:
        """The list of assays taken during the context"""
        return [d.copy() for d in self._during]

    @abstractmethod
    def assay(self) -> Assey:
        """Take an assay of the current state"""
        raise NotImplementedError()

    def _run(self, interval: float) -> None:
        while self._running:
            time.sleep(interval)
            self._during[-1].append(self.assay())

    def __enter__(self) -> Self:
        """Take an initial assay and start monitoring if interval is set"""
        self._during.append([self.assay()])
        if self._interval is not None:
            self._running = True
            self._thread = Thread(target=self._run, args=(self._interval,))
            self._thread.start()
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,  # noqa: F841
        value: BaseException | None,  # noqa: F841
        traceback: TracebackType | None,  # noqa: F841
    ) -> None:
        """Stop monitoring and take a final assay when exiting the context manager"""
        if self._interval is not None:
            self._running = False
            if self._thread:
                self._thread.join()
