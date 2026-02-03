from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.shared.domain.entities import Entity

from .constants import MovementType
from .exceptions import InvalidMovementTypeException


@dataclass
class Movement(Entity):
    product_id: int
    quantity: int
    type: MovementType
    id: Optional[int] = None
    reason: Optional[str] = None
    date: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.quantity == 0:
            raise InvalidMovementTypeException("La cantidad no puede ser cero")

        if self.type == MovementType.IN and self.quantity < 0:
            raise InvalidMovementTypeException(
                "La cantidad debe ser positiva para movimientos de entrada"
            )

        if self.type == MovementType.OUT and self.quantity > 0:
            raise InvalidMovementTypeException(
                "La cantidad debe ser negativa para movimientos de salida"
            )
