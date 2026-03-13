"""Pydantic schemas para validacion POS Sales"""

from pydantic import AliasChoices, BaseModel, Field


class POSSaleRequest(BaseModel):
    """Schema para crear una venta desde POS"""

    customer_id: int | None = Field(
        None,
        gt=0,
        description="ID del cliente (opcional si es consumidor final)",
        validation_alias=AliasChoices("customerId", "customer_id"),
        serialization_alias="customerId",
    )
    is_final_consumer: bool = Field(
        False,
        description="Indica si es consumidor final",
        validation_alias=AliasChoices("isFinalConsumer", "is_final_consumer"),
        serialization_alias="isFinalConsumer",
    )
    notes: str | None = Field(None, max_length=512, description="Notas adicionales")
    created_by: str | None = Field(
        None,
        max_length=64,
        description="Usuario que crea",
        validation_alias=AliasChoices("createdBy", "created_by"),
        serialization_alias="createdBy",
    )
