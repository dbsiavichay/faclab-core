from dataclasses import dataclass

from src.inventory.stock.domain.exceptions import InsufficientStock
from src.shared.domain.entities import Entity


@dataclass
class Stock(Entity):
    product_id: int
    quantity: int
    id: int | None = None
    location: str | None = None

    def update_quantity(self, quantity: int):
        new_quantity = self.quantity + quantity
        if new_quantity < 0:
            raise InsufficientStock(self.product_id, quantity)
        self.quantity = new_quantity
        return self
