from dataclasses import dataclass
from typing import Any

from src.shared.domain.events import DomainEvent


@dataclass
class AdjustmentConfirmed(DomainEvent):
    adjustment_id: int = 0
    warehouse_id: int = 0
    items_adjusted: int = 0

    def _payload(self) -> dict[str, Any]:
        return {
            "adjustment_id": self.adjustment_id,
            "warehouse_id": self.warehouse_id,
            "items_adjusted": self.items_adjusted,
        }
