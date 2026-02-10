from dataclasses import dataclass
from typing import Any, Dict

from src.shared.domain.events import DomainEvent


@dataclass
class CustomerCreated(DomainEvent):
    customer_id: int = 0
    name: str = ""
    tax_id: str = ""

    def _payload(self) -> Dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "tax_id": self.tax_id,
        }


@dataclass
class CustomerUpdated(DomainEvent):
    customer_id: int = 0
    name: str = ""

    def _payload(self) -> Dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
        }


@dataclass
class CustomerActivated(DomainEvent):
    customer_id: int = 0

    def _payload(self) -> Dict[str, Any]:
        return {"customer_id": self.customer_id}


@dataclass
class CustomerDeactivated(DomainEvent):
    customer_id: int = 0
    reason: str = ""

    def _payload(self) -> Dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "reason": self.reason,
        }
