from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class WarehouseRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str
    code: str
    address: str | None = None
    city: str | None = None
    country: str | None = None
    is_active: bool = True
    is_default: bool = False
    manager: str | None = None
    phone: str | None = None
    email: str | None = None


class WarehouseResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    name: str
    code: str
    address: str | None = None
    city: str | None = None
    country: str | None = None
    is_active: bool
    is_default: bool
    manager: str | None = None
    phone: str | None = None
    email: str | None = None
