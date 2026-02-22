from pydantic import AliasChoices, BaseModel, Field

from src.shared.infra.validators import QueryParams


class StockResponse(BaseModel):
    id: int
    product_id: int = Field(
        ...,
        ge=1,
        description="Product ID",
        validation_alias=AliasChoices("productId", "product_id"),
        serialization_alias="productId",
    )
    quantity: int
    location_id: int | None = Field(
        None,
        validation_alias=AliasChoices("locationId", "location_id"),
        serialization_alias="locationId",
    )
    reserved_quantity: int = Field(
        0,
        validation_alias=AliasChoices("reservedQuantity", "reserved_quantity"),
        serialization_alias="reservedQuantity",
    )


class StockQueryParams(QueryParams):
    product_id: int | None = Field(
        None,
        ge=1,
        validation_alias=AliasChoices("productId", "product_id"),
        serialization_alias="productId",
    )
    location_id: int | None = Field(
        None,
        ge=1,
        validation_alias=AliasChoices("locationId", "location_id"),
        serialization_alias="locationId",
    )
