from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from typing_extensions import Self
from types import TracebackType

T = TypeVar("T")


class Observer(ABC, Generic[T]):
    def __init__(self) -> None:
        self._before: list[T] = []
        self._after: list[T] = []

    @property
    def before(self) -> list[T]:
        """The list of assays taken before entering the context"""
        return self._before.copy()

    @property
    def after(self) -> list[T]:
        """The list of assays taken after exiting the context"""
        return self._after.copy()

    @abstractmethod
    def assay(self) -> T:
        """Take an assay of the current state"""
        raise NotImplementedError()

    def __enter__(self) -> Self:
        """Take an initial assay when entering the context manager"""
        self._before.append(self.assay())
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,  # noqa: F841
        value: BaseException | None,  # noqa: F841
        traceback: TracebackType | None,  # noqa: F841
    ) -> None:
        """Take a final assay when exiting the context manager"""
        end_value = self.assay()
        self._after.append(end_value)
