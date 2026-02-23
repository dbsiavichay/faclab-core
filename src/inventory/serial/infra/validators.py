from datetime import datetime

from pydantic import AliasChoices, BaseModel, Field


class SerialNumberRequest(BaseModel):
    product_id: int = Field(
        ...,
        ge=1,
        description="Product ID",
        validation_alias=AliasChoices("productId", "product_id"),
        serialization_alias="productId",
    )
    serial_number: str = Field(
        ...,
        max_length=128,
        description="Serial number",
        validation_alias=AliasChoices("serialNumber", "serial_number"),
        serialization_alias="serialNumber",
    )
    lot_id: int | None = Field(
        None,
        ge=1,
        description="Associated lot ID",
        validation_alias=AliasChoices("lotId", "lot_id"),
        serialization_alias="lotId",
    )
    location_id: int | None = Field(
        None,
        ge=1,
        description="Storage location ID",
        validation_alias=AliasChoices("locationId", "location_id"),
        serialization_alias="locationId",
    )
    notes: str | None = Field(None, max_length=1024)


class SerialStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="New status for the serial number")


class SerialNumberResponse(BaseModel):
    id: int = Field(ge=1)
    product_id: int = Field(
        ge=1,
        validation_alias=AliasChoices("productId", "product_id"),
        serialization_alias="productId",
    )
    serial_number: str = Field(
        validation_alias=AliasChoices("serialNumber", "serial_number"),
        serialization_alias="serialNumber",
    )
    status: str
    lot_id: int | None = Field(
        None,
        validation_alias=AliasChoices("lotId", "lot_id"),
        serialization_alias="lotId",
    )
    location_id: int | None = Field(
        None,
        validation_alias=AliasChoices("locationId", "location_id"),
        serialization_alias="locationId",
    )
    purchase_order_id: int | None = Field(
        None,
        validation_alias=AliasChoices("purchaseOrderId", "purchase_order_id"),
        serialization_alias="purchaseOrderId",
    )
    sale_id: int | None = Field(
        None,
        validation_alias=AliasChoices("saleId", "sale_id"),
        serialization_alias="saleId",
    )
    notes: str | None = None
    created_at: datetime | None = Field(
        None,
        validation_alias=AliasChoices("createdAt", "created_at"),
        serialization_alias="createdAt",
    )
