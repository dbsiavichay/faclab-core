from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

# ---------------------------------------------------------------------------
# Valuation
# ---------------------------------------------------------------------------


class ValuationItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    product_id: int
    product_name: str
    sku: str
    quantity: int
    average_cost: Decimal
    total_value: Decimal


class InventoryValuationResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    total_value: Decimal
    as_of_date: date
    items: list[ValuationItemResponse]


class ValuationQueryParams(BaseModel):
    warehouse_id: int | None = Field(None, ge=1, alias="warehouseId")
    as_of_date: date | None = Field(None, alias="asOfDate")

    model_config = ConfigDict(populate_by_name=True)


# ---------------------------------------------------------------------------
# Rotation
# ---------------------------------------------------------------------------


class ProductRotationResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    product_id: int
    product_name: str
    sku: str
    total_in: int
    total_out: int
    current_stock: int
    turnover_rate: Decimal
    days_of_stock: int | None = None


class RotationQueryParams(BaseModel):
    from_date: date = Field(default_factory=lambda: date.today().replace(day=1))
    to_date: date = Field(default_factory=date.today)
    warehouse_id: int | None = Field(None, ge=1, alias="warehouseId")

    model_config = ConfigDict(populate_by_name=True)


# ---------------------------------------------------------------------------
# Movement History
# ---------------------------------------------------------------------------


class MovementHistoryItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    id: int
    product_id: int
    product_name: str
    sku: str
    quantity: int
    type: str
    location_id: int | None = None
    source_location_id: int | None = None
    reference_type: str | None = None
    reference_id: int | None = None
    reason: str | None = None
    date: datetime | None = None
    created_at: datetime | None = None


class MovementHistoryResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    total: int
    limit: int
    offset: int
    items: list[MovementHistoryItemResponse]


class MovementHistoryQueryParams(BaseModel):
    product_id: int | None = Field(None, ge=1, alias="productId")
    type: str | None = None
    from_date: date | None = Field(None, alias="fromDate")
    to_date: date | None = Field(None, alias="toDate")
    warehouse_id: int | None = Field(None, ge=1, alias="warehouseId")
    limit: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)

    model_config = ConfigDict(populate_by_name=True)


# ---------------------------------------------------------------------------
# Warehouse Summary
# ---------------------------------------------------------------------------


class WarehouseSummaryResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    warehouse_id: int
    warehouse_name: str
    warehouse_code: str
    total_products: int
    total_quantity: int
    reserved_quantity: int
    available_quantity: int
    total_value: Decimal


class SummaryQueryParams(BaseModel):
    warehouse_id: int | None = Field(None, ge=1, alias="warehouseId")

    model_config = ConfigDict(populate_by_name=True)
