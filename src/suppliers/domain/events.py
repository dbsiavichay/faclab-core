from dataclasses import dataclass
from typing import Any

from src.shared.domain.events import DomainEvent


@dataclass
class SupplierCreated(DomainEvent):
    supplier_id: int = 0
    name: str = ""
    tax_id: str = ""

    def _payload(self) -> dict[str, Any]:
        return {
            "supplier_id": self.supplier_id,
            "name": self.name,
            "tax_id": self.tax_id,
        }


@dataclass
class SupplierActivated(DomainEvent):
    supplier_id: int = 0

    def _payload(self) -> dict[str, Any]:
        return {"supplier_id": self.supplier_id}


@dataclass
class SupplierDeactivated(DomainEvent):
    supplier_id: int = 0
    reason: str | None = None

    def _payload(self) -> dict[str, Any]:
        return {
            "supplier_id": self.supplier_id,
            "reason": self.reason,
        }
