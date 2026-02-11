from typing import Any

from src.customers.infra.models import CustomerModel
from src.shared.domain.specifications import Specification


class ActiveCustomers(Specification):
    def is_satisfied_by(self, candidate: Any) -> bool:
        return getattr(candidate, "is_active", False) is True

    def to_sql_criteria(self) -> list[Any]:
        return [CustomerModel.is_active == True]  # noqa: E712


class CustomersByType(Specification):
    def __init__(self, tax_type: int):
        self.tax_type = tax_type

    def is_satisfied_by(self, candidate: Any) -> bool:
        return getattr(candidate, "tax_type", None) == self.tax_type

    def to_sql_criteria(self) -> list[Any]:
        return [CustomerModel.tax_type == self.tax_type]
