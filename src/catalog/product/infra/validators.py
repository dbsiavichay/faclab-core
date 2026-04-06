from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.shared.infra.validators import DecimalNumber, QueryParams


# Requests
class CategoryRequest(BaseModel):
    name: str
    description: str | None = None


class ProductRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str
    sku: str
    description: str | None = None
    barcode: str | None = None
    category_id: int | None = Field(None, ge=1)
    unit_of_measure_id: int | None = Field(None, ge=1)
    purchase_price: DecimalNumber | None = Field(None, ge=0)
    sale_price: DecimalNumber | None = Field(None, ge=0)
    tax_rate: DecimalNumber = Field(Decimal("15.00"), ge=0, le=100)
    is_active: bool = True
    is_service: bool = False
    min_stock: int = Field(0, ge=0)
    max_stock: int | None = Field(None, ge=0)
    reorder_point: int = Field(0, ge=0)
    lead_time_days: int | None = Field(None, ge=0)


# Responses
class CategoryResponse(CategoryRequest):
    id: int = Field(ge=1)


class ProductResponse(ProductRequest):
    id: int = Field(ge=1)


# Query Params
class CategoryQueryParams(QueryParams):
    pass


class ProductQueryParams(QueryParams):
    category_id: int | None = Field(None, ge=1)
