
from pydantic import BaseModel, Field


class QueryParams(BaseModel):
    limit: int | None = Field(100, ge=1, le=1000)
    offset: int | None = Field(0, ge=0)
