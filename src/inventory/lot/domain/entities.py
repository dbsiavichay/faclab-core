from dataclasses import dataclass
from datetime import date, datetime

from src.shared.domain.entities import Entity


@dataclass
class Lot(Entity):
    product_id: int
    lot_number: str
    id: int | None = None
    manufacture_date: date | None = None
    expiration_date: date | None = None
    initial_quantity: int = 0
    current_quantity: int = 0
    notes: str | None = None
    created_at: datetime | None = None

    @property
    def is_expired(self) -> bool:
        if self.expiration_date is None:
            return False
        return date.today() > self.expiration_date

    @property
    def days_to_expiry(self) -> int | None:
        if self.expiration_date is None:
            return None
        return (self.expiration_date - date.today()).days


@dataclass
class MovementLotItem(Entity):
    movement_id: int
    lot_id: int
    quantity: int
    id: int | None = None
