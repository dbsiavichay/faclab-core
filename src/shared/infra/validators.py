from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class QueryParams(BaseModel):
    limit: int | None = Field(100, ge=1, le=1000)
    offset: int | None = Field(0, ge=0)


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    items: list[T]
