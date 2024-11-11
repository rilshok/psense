import time
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from typing_extensions import Self
from types import TracebackType
from threading import Thread

T = TypeVar("T")


class Observer(ABC, Generic[T]):
    def __init__(self, interval: float | None = None) -> None:
        self._before: list[T] = []
        self._during: list[list[T]] = []
        self._after: list[T] = []
        self._interval = interval
        self._running = False
        self._thread: Thread | None = None

    @property
    def before(self) -> list[T]:
        """The list of assays taken before entering the context"""
        return self._before.copy()

    @property
    def during(self) -> list[list[T]]:
        """The list of assays taken during the context"""
        return [d.copy() for d in self._during]

    @property
    def after(self) -> list[T]:
        """The list of assays taken after exiting the context"""
        return self._after.copy()

    @abstractmethod
    def assay(self) -> T:
        """Take an assay of the current state"""
        raise NotImplementedError()

    def _run(self, interval: float) -> None:
        while self._running:
            time.sleep(interval / 2)
            self._during[-1].append(self.assay())
            time.sleep(interval / 2)

    def __enter__(self) -> Self:
        """Take an initial assay and start monitoring if interval is set"""
        self._before.append(self.assay())
        self._during.append([])
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
        self._after.append(self.assay())
