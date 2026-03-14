from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from src.shared.domain.entities import Entity


class CashMovementType(StrEnum):
    IN = "IN"
    OUT = "OUT"


@dataclass
class CashMovement(Entity):
    shift_id: int
    type: CashMovementType
    amount: Decimal
    reason: str | None = None
    performed_by: str | None = None
    created_at: datetime | None = None
    id: int | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
