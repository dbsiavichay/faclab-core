from typing import TypedDict


class LocationOutput(TypedDict):
    id: int
    warehouse_id: int
    name: str
    code: str
    type: str
    is_active: bool
    capacity: int | None
