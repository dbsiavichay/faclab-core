from decimal import Decimal
from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer
from pydantic.alias_generators import to_camel

DecimalNumber = Annotated[
    Decimal,
    PlainSerializer(lambda v: float(v), return_type=float),
]

T = TypeVar("T")


class QueryParams(BaseModel):
    limit: int | None = Field(100, ge=1, le=1000)
    offset: int | None = Field(0, ge=0)


class Meta(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    request_id: str
    timestamp: str

    def with_pagination(self, total: int, limit: int, offset: int) -> "PaginatedMeta":
        return PaginatedMeta(
            request_id=self.request_id,
            timestamp=self.timestamp,
            pagination=PaginationMeta(total=total, limit=limit, offset=offset),
        )


class PaginationMeta(BaseModel):
    total: int
    limit: int
    offset: int


class PaginatedMeta(Meta):
    pagination: PaginationMeta


class DataResponse(BaseModel, Generic[T]):
    data: T
    meta: Meta


class ListResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: Meta


class PaginatedDataResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: PaginatedMeta


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None


class ErrorResponse(BaseModel):
    errors: list[ErrorDetail]
    meta: Meta
