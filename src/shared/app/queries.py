from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar


@dataclass
class Query:
    pass


TQuery = TypeVar("TQuery", bound=Query)
TResult = TypeVar("TResult")


class QueryHandler(Generic[TQuery, TResult], ABC):
    @abstractmethod
    def handle(self, query: TQuery) -> TResult:
        raise NotImplementedError
