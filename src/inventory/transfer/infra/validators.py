from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.shared.infra.validators import QueryParams


class CreateTransferRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    source_location_id: int
    destination_location_id: int
    notes: str | None = None
    requested_by: str | None = None


class UpdateTransferRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    notes: str | None = None
    requested_by: str | None = None


class AddTransferItemRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    product_id: int
    quantity: int = Field(gt=0)
    lot_id: int | None = None
    notes: str | None = None


class UpdateTransferItemRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    quantity: int | None = Field(None, gt=0)
    notes: str | None = None


class TransferResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    id: int
    source_location_id: int
    destination_location_id: int
    status: str
    transfer_date: datetime | None = None
    requested_by: str | None = None
    notes: str | None = None
    created_at: datetime | None = None


class TransferItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    id: int
    transfer_id: int
    product_id: int
    quantity: int
    lot_id: int | None = None
    notes: str | None = None


class TransferQueryParams(QueryParams):
    status: str | None = None
    source_location_id: int | None = Field(
        None,
        ge=1,
        validation_alias=AliasChoices("sourceLocationId", "source_location_id"),
        serialization_alias="sourceLocationId",
    )
