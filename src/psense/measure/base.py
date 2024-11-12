from abc import ABC, abstractmethod
from collections.abc import Iterable

Assey = tuple[float | int, ...]


class Measurer(ABC):
    def __init__(self, name: str, keys: tuple[str, ...]) -> None:
        self._name = name
        self._keys = keys

    @abstractmethod
    def assey(self) -> Assey:
        """Take an assay of the current state"""
        raise NotImplementedError()

    @property
    def name(self) -> str:
        """Return the name of the measurer"""
        return self._name

    @property
    def keys(self) -> tuple[str, ...]:
        """Return the keys"""
        return self._keys

    @property
    def keys_full(self) -> tuple[str, ...]:
        """Return the full keys"""
        if self.name:
            return tuple(f"{self.name}/{key}" for key in self.keys)
        return self.keys


class MeasurerGroup(Measurer):
    def __init__(self, mesurers: Iterable[Measurer]) -> None:
        mesurers = list(mesurers)
        if len(set(measurer.name for measurer in mesurers)) != len(mesurers):
            msg = "Measurers must have unique names."
            raise ValueError(msg)
        self._mesurers = list(mesurers)
        super().__init__(
            name="",
            keys=tuple(key for measurer in self._mesurers for key in measurer.keys_full),
        )

    def assey(self) -> Assey:
        return tuple(value for measurer in self._mesurers for value in measurer.assey())
