from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class UnitOfMeasureRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str
    symbol: str
    description: str | None = None
    is_active: bool = True


class UnitOfMeasureResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    name: str
    symbol: str
    description: str | None = None
    is_active: bool
