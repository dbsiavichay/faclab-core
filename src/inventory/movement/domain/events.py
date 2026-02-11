from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from src.shared.domain.events import DomainEvent


@dataclass
class MovementCreated(DomainEvent):
    """
    Evento emitido cuando se crea un movimiento de inventario.
    Este evento desencadena la actualización del stock correspondiente.
    """

    aggregate_id: int = 0  # movement_id
    product_id: int = 0
    quantity: int = 0
    type: str = ""  # "in" or "out"
    reason: Optional[str] = None
    date: Optional[datetime] = None

    def _payload(self) -> Dict[str, Any]:
        return {
            "movement_id": self.aggregate_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "type": self.type,
            "reason": self.reason,
            "date": self.date.isoformat() if self.date else None,
        }
