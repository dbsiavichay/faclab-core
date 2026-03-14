from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from src.shared.domain.events import DomainEvent


@dataclass
class RefundCompleted(DomainEvent):
    refund_id: int = 0
    original_sale_id: int = 0
    items: list[dict[str, Any]] = field(default_factory=list)
    total: Decimal = Decimal("0")
    source: str = "pos"

    def _payload(self) -> dict[str, Any]:
        return {
            "refund_id": self.refund_id,
            "original_sale_id": self.original_sale_id,
            "items": self.items,
            "total": self.total,
            "source": self.source,
        }
