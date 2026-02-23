from dataclasses import dataclass
from typing import Any

from src.shared.domain.events import DomainEvent


@dataclass
class StockTransferConfirmed(DomainEvent):
    transfer_id: int = 0
    source_location_id: int = 0
    destination_location_id: int = 0
    items_reserved: int = 0

    def _payload(self) -> dict[str, Any]:
        return {
            "transfer_id": self.transfer_id,
            "source_location_id": self.source_location_id,
            "destination_location_id": self.destination_location_id,
            "items_reserved": self.items_reserved,
        }


@dataclass
class StockTransferReceived(DomainEvent):
    transfer_id: int = 0
    source_location_id: int = 0
    destination_location_id: int = 0
    items_transferred: int = 0

    def _payload(self) -> dict[str, Any]:
        return {
            "transfer_id": self.transfer_id,
            "source_location_id": self.source_location_id,
            "destination_location_id": self.destination_location_id,
            "items_transferred": self.items_transferred,
        }


@dataclass
class StockTransferCancelled(DomainEvent):
    transfer_id: int = 0
    was_confirmed: bool = False

    def _payload(self) -> dict[str, Any]:
        return {
            "transfer_id": self.transfer_id,
            "was_confirmed": self.was_confirmed,
        }
