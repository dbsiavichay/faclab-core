from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.shared.infra.validators import DecimalNumber, QueryParams

# ---------------------------------------------------------------------------
# Valuation
# ---------------------------------------------------------------------------


class ValuationItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    product_id: int
    product_name: str
    sku: str
    quantity: int
    average_cost: DecimalNumber
    total_value: DecimalNumber


class InventoryValuationResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    total_value: DecimalNumber
    as_of_date: date
    items: list[ValuationItemResponse]


class ValuationQueryParams(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    warehouse_id: int | None = Field(None, ge=1)
    as_of_date: date | None = None


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
    turnover_rate: DecimalNumber
    days_of_stock: int | None = None


class RotationQueryParams(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    from_date: date = Field(default_factory=lambda: date.today().replace(day=1))
    to_date: date = Field(default_factory=date.today)
    warehouse_id: int | None = Field(None, ge=1)


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


class MovementHistoryQueryParams(QueryParams):
    limit: int | None = Field(50, ge=1, le=500)
    product_id: int | None = Field(None, ge=1)
    type: str | None = None
    from_date: date | None = None
    to_date: date | None = None
    warehouse_id: int | None = Field(None, ge=1)


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
    total_value: DecimalNumber


class SummaryQueryParams(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    warehouse_id: int | None = Field(None, ge=1)
