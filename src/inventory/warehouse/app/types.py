from typing import TypedDict


class WarehouseOutput(TypedDict):
    id: int
    name: str
    code: str
    address: str | None
    city: str | None
    country: str | None
    is_active: bool
    is_default: bool
    manager: str | None
    phone: str | None
    email: str | None
