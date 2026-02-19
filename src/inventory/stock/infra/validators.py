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
    location: str | None = None


class StockQueryParams(QueryParams):
    product_id: int | None = Field(
        None,
        ge=1,
        validation_alias=AliasChoices("productId", "product_id"),
        serialization_alias="productId",
    )
