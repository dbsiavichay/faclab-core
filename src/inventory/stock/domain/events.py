from dataclasses import dataclass
from typing import Any

from src.shared.domain.events import DomainEvent


@dataclass
class StockCreated(DomainEvent):
    """
    Evento emitido cuando se crea un nuevo registro de stock.
    Ocurre cuando se registra el primer movimiento para un producto.
    """

    aggregate_id: int = 0  # stock_id
    product_id: int = 0
    quantity: int = 0
    location: str | None = None

    def _payload(self) -> dict[str, Any]:
        return {
            "stock_id": self.aggregate_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "location": self.location,
        }


@dataclass
class StockUpdated(DomainEvent):
    """
    Evento emitido cuando se actualiza la cantidad de un stock existente.
    Contiene tanto la cantidad anterior como la nueva para auditoría.
    """

    aggregate_id: int = 0  # stock_id
    product_id: int = 0
    old_quantity: int = 0
    new_quantity: int = 0
    location: str | None = None

    def _payload(self) -> dict[str, Any]:
        return {
            "stock_id": self.aggregate_id,
            "product_id": self.product_id,
            "old_quantity": self.old_quantity,
            "new_quantity": self.new_quantity,
            "location": self.location,
        }
