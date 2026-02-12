from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar


@dataclass
class Command:
    pass


TCommand = TypeVar("TCommand", bound=Command)
TResult = TypeVar("TResult")


class CommandHandler(Generic[TCommand, TResult], ABC):
    @abstractmethod
    def handle(self, command: TCommand) -> TResult:
        raise NotImplementedError
