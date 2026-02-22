from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from src.inventory.location.domain.entities import LocationType


class LocationRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    warehouse_id: int
    name: str
    code: str
    type: LocationType = LocationType.STORAGE
    is_active: bool = True
    capacity: int | None = None


class LocationResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    warehouse_id: int
    name: str
    code: str
    type: LocationType
    is_active: bool
    capacity: int | None = None
