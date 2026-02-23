from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum

from src.shared.domain.entities import Entity
from src.shared.domain.exceptions import DomainError


class SerialStatus(StrEnum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"
    RETURNED = "returned"
    SCRAPPED = "scrapped"


@dataclass
class SerialNumber(Entity):
    product_id: int
    serial_number: str
    status: SerialStatus = SerialStatus.AVAILABLE
    id: int | None = None
    lot_id: int | None = None
    location_id: int | None = None
    purchase_order_id: int | None = None
    sale_id: int | None = None
    created_at: datetime | None = None
    notes: str | None = None

    def mark_sold(self) -> "SerialNumber":
        if self.status != SerialStatus.AVAILABLE:
            raise DomainError(
                f"Cannot mark serial '{self.serial_number}' as sold. Current status: '{self.status.value}'. Only AVAILABLE serials can be sold."
            )
        return replace(self, status=SerialStatus.SOLD)

    def mark_reserved(self) -> "SerialNumber":
        if self.status != SerialStatus.AVAILABLE:
            raise DomainError(
                f"Cannot mark serial '{self.serial_number}' as reserved. Current status: '{self.status.value}'. Only AVAILABLE serials can be reserved."
            )
        return replace(self, status=SerialStatus.RESERVED)

    def mark_returned(self) -> "SerialNumber":
        if self.status != SerialStatus.SOLD:
            raise DomainError(
                f"Cannot mark serial '{self.serial_number}' as returned. Current status: '{self.status.value}'. Only SOLD serials can be returned."
            )
        return replace(self, status=SerialStatus.RETURNED)

    def mark_scrapped(self) -> "SerialNumber":
        return replace(self, status=SerialStatus.SCRAPPED)
