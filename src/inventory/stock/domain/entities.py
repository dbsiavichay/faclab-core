from dataclasses import dataclass, replace

from src.inventory.stock.domain.exceptions import InsufficientStockError
from src.shared.domain.entities import Entity


@dataclass
class Stock(Entity):
    product_id: int
    quantity: int
    id: int | None = None
    location_id: int | None = None
    reserved_quantity: int = 0

    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity

    def update_quantity(self, delta: int) -> "Stock":
        new_quantity = self.quantity + delta
        if new_quantity < 0:
            raise InsufficientStockError(self.product_id, delta)
        return replace(self, quantity=new_quantity)
