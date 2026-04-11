from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.shared.infra.validators import QueryParams


class UnitOfMeasureRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str = Field(description="Unit name (e.g. Kilogram, Liter, Box)")
    symbol: str = Field(description="Abbreviation (e.g. kg, L, box)")
    description: str | None = Field(None, description="Optional description")
    is_active: bool = Field(True, description="Whether the unit is active")


class UnitOfMeasureResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int = Field(description="Unit of measure ID")
    name: str = Field(description="Unit name")
    symbol: str = Field(description="Abbreviation")
    description: str | None = Field(None, description="Optional description")
    is_active: bool = Field(description="Whether the unit is active")


# Query Params
class UnitOfMeasureQueryParams(QueryParams):
    is_active: bool | None = Field(None, description="Filter by active status")
