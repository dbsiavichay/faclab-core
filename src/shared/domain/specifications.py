from abc import ABC, abstractmethod
from typing import Any, List


class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def to_sql_criteria(self) -> List[Any]:
        raise NotImplementedError

    def __and__(self, other: "Specification") -> "AndSpecification":
        return AndSpecification(self, other)

    def __or__(self, other: "Specification") -> "OrSpecification":
        return OrSpecification(self, other)

    def __invert__(self) -> "NotSpecification":
        return NotSpecification(self)


class AndSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: Any) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(
            candidate
        )

    def to_sql_criteria(self) -> List[Any]:
        return self.left.to_sql_criteria() + self.right.to_sql_criteria()


class OrSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: Any) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(
            candidate
        )

    def to_sql_criteria(self) -> List[Any]:
        from sqlalchemy import or_

        left_criteria = self.left.to_sql_criteria()
        right_criteria = self.right.to_sql_criteria()
        return [or_(*left_criteria, *right_criteria)]


class NotSpecification(Specification):
    def __init__(self, spec: Specification):
        self.spec = spec

    def is_satisfied_by(self, candidate: Any) -> bool:
        return not self.spec.is_satisfied_by(candidate)

    def to_sql_criteria(self) -> List[Any]:
        from sqlalchemy import and_, not_

        criteria = self.spec.to_sql_criteria()
        return [not_(and_(*criteria))]
