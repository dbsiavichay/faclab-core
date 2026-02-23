from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.shared.infra.validators import QueryParams


class CreateAdjustmentRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    warehouse_id: int
    reason: str
    notes: str | None = None
    adjusted_by: str | None = None


class UpdateAdjustmentRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    notes: str | None = None
    adjusted_by: str | None = None


class AddAdjustmentItemRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    product_id: int
    location_id: int
    actual_quantity: int
    lot_id: int | None = None
    notes: str | None = None


class UpdateAdjustmentItemRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    actual_quantity: int | None = None
    notes: str | None = None


class AdjustmentResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    id: int
    warehouse_id: int
    reason: str
    status: str
    adjustment_date: datetime | None = None
    notes: str | None = None
    adjusted_by: str | None = None
    created_at: datetime | None = None


class AdjustmentItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    id: int
    adjustment_id: int
    product_id: int
    location_id: int
    expected_quantity: int
    actual_quantity: int
    difference: int
    lot_id: int | None = None
    notes: str | None = None


class AdjustmentQueryParams(QueryParams):
    status: str | None = None
    warehouse_id: int | None = Field(
        None,
        ge=1,
        validation_alias=AliasChoices("warehouseId", "warehouse_id"),
        serialization_alias="warehouseId",
    )
