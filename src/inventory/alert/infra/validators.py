from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class StockAlertResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    type: str
    product_id: int
    product_name: str
    sku: str
    current_quantity: int
    threshold: int
    warehouse_id: int | None = None
    lot_id: int | None = None
    days_to_expiry: int | None = None


class StockAlertQueryParams(BaseModel):
    warehouse_id: int | None = Field(
        None,
        ge=1,
        validation_alias=AliasChoices("warehouseId", "warehouse_id"),
        serialization_alias="warehouseId",
    )


class ExpiringLotsQueryParams(BaseModel):
    days: int = Field(30, ge=1)
