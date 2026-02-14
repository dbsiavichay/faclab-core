from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.shared.domain.specifications import Specification

T = TypeVar("T")


class Repository(Generic[T], ABC):
    @abstractmethod
    def create(self, entity: T) -> T:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: T) -> T:
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: int) -> T | None:
        raise NotImplementedError

    @abstractmethod
    def first(self, **kwargs) -> T | None:
        raise NotImplementedError

    @abstractmethod
    def filter_by(
        self, limit: int | None = None, offset: int | None = None, **kwargs
    ) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    def filter_by_spec(
        self,
        spec: Specification,
        order_by: str | None = None,
        desc_order: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[T]:
        raise NotImplementedError
