from datetime import date, datetime
from decimal import Decimal
from typing import TypedDict


class ValuationItemOutput(TypedDict):
    product_id: int
    product_name: str
    sku: str
    quantity: int
    average_cost: Decimal
    total_value: Decimal


class InventoryValuationOutput(TypedDict):
    total_value: Decimal
    as_of_date: date
    items: list[ValuationItemOutput]


class ProductRotationOutput(TypedDict):
    product_id: int
    product_name: str
    sku: str
    total_in: int
    total_out: int
    current_stock: int
    turnover_rate: Decimal
    days_of_stock: int | None


class MovementHistoryItemOutput(TypedDict):
    id: int
    product_id: int
    product_name: str
    sku: str
    quantity: int
    type: str
    location_id: int | None
    source_location_id: int | None
    reference_type: str | None
    reference_id: int | None
    reason: str | None
    date: datetime | None
    created_at: datetime | None


class MovementHistoryOutput(TypedDict):
    total: int
    limit: int
    offset: int
    items: list[MovementHistoryItemOutput]


class WarehouseSummaryOutput(TypedDict):
    warehouse_id: int
    warehouse_name: str
    warehouse_code: str
    total_products: int
    total_quantity: int
    reserved_quantity: int
    available_quantity: int
    total_value: Decimal
