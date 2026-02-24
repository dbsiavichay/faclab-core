from dataclasses import dataclass
from enum import StrEnum


class AlertType(StrEnum):
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    REORDER_POINT = "reorder_point"


@dataclass
class StockAlert:
    type: AlertType
    product_id: int
    product_name: str
    sku: str
    current_quantity: int
    threshold: int
    warehouse_id: int | None = None
    lot_id: int | None = None
    days_to_expiry: int | None = None
