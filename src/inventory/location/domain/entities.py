from dataclasses import dataclass
from enum import StrEnum

from src.shared.domain.entities import Entity


class LocationType(StrEnum):
    STORAGE = "storage"
    RECEIVING = "receiving"
    SHIPPING = "shipping"
    QUALITY = "quality"
    DAMAGED = "damaged"


@dataclass
class Location(Entity):
    warehouse_id: int
    name: str
    code: str
    id: int | None = None
    type: LocationType = LocationType.STORAGE
    is_active: bool = True
    capacity: int | None = None
