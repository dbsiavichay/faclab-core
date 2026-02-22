from datetime import datetime

from pydantic import AliasChoices, BaseModel, Field, field_validator, model_validator

from src.inventory.movement.domain.constants import MovementType
from src.inventory.movement.domain.exceptions import InvalidMovementTypeError
from src.shared.infra.validators import QueryParams


class MovementBase(BaseModel):
    product_id: int = Field(
        ...,
        ge=1,
        description="Product ID",
        validation_alias=AliasChoices("productId", "product_id"),
        serialization_alias="productId",
    )
    quantity: int = Field(..., ge=1, description="Quantity")
    type: MovementType
    location_id: int | None = Field(
        None,
        validation_alias=AliasChoices("locationId", "location_id"),
        serialization_alias="locationId",
    )
    reference_type: str | None = Field(
        None,
        validation_alias=AliasChoices("referenceType", "reference_type"),
        serialization_alias="referenceType",
    )
    reference_id: int | None = Field(
        None,
        validation_alias=AliasChoices("referenceId", "reference_id"),
        serialization_alias="referenceId",
    )
    reason: str | None = None
    date: datetime | None = None


class MovementRequest(MovementBase):
    @field_validator("quantity", mode="after")
    @classmethod
    def validate_quantity_not_zero(cls, v):
        if v == 0:
            raise InvalidMovementTypeError("La cantidad no puede ser cero")
        return v

    @model_validator(mode="after")
    def validate_quantity_by_movement_type(self) -> "MovementRequest":
        if self.type == MovementType.IN and self.quantity < 0:
            raise InvalidMovementTypeError(
                "La cantidad debe ser positiva para movimientos de entrada"
            )
        elif self.type == MovementType.OUT and self.quantity > 0:
            raise InvalidMovementTypeError(
                "La cantidad debe ser negativa para movimientos de salida"
            )
        return self


class MovementResponse(MovementBase):
    id: int


class MovementQueryParams(QueryParams):
    product_id: int | None = Field(
        None,
        ge=1,
        validation_alias=AliasChoices("productId", "product_id"),
        serialization_alias="productId",
    )
    type: MovementType | None = None
    from_date: datetime | None = Field(
        None,
        validation_alias=AliasChoices("fromDate", "from_date"),
        serialization_alias="fromDate",
    )
    to_date: datetime | None = Field(
        None,
        validation_alias=AliasChoices("toDate", "to_date"),
        serialization_alias="toDate",
    )
