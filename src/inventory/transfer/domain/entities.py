from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum

from src.shared.domain.entities import Entity
from src.shared.domain.exceptions import DomainError


class TransferStatus(StrEnum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    RECEIVED = "received"
    CANCELLED = "cancelled"


@dataclass
class StockTransfer(Entity):
    source_location_id: int
    destination_location_id: int
    status: TransferStatus = TransferStatus.DRAFT
    id: int | None = None
    transfer_date: datetime | None = None
    requested_by: str | None = None
    notes: str | None = None
    created_at: datetime | None = None

    def confirm(self) -> "StockTransfer":
        if self.status != TransferStatus.DRAFT:
            raise DomainError("Solo transferencias en DRAFT pueden confirmarse")
        return replace(self, status=TransferStatus.CONFIRMED)

    def receive(self) -> "StockTransfer":
        if self.status != TransferStatus.CONFIRMED:
            raise DomainError("Solo transferencias CONFIRMED pueden recibirse")
        return replace(self, status=TransferStatus.RECEIVED)

    def cancel(self) -> "StockTransfer":
        if self.status == TransferStatus.RECEIVED:
            raise DomainError("No se puede cancelar una transferencia ya recibida")
        return replace(self, status=TransferStatus.CANCELLED)


@dataclass
class StockTransferItem(Entity):
    transfer_id: int
    product_id: int
    quantity: int
    id: int | None = None
    lot_id: int | None = None
    notes: str | None = None
