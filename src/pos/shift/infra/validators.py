"""Pydantic schemas para validacion y serializacion de Shifts"""

from datetime import datetime
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from src.shared.infra.validators import DecimalNumber, QueryParams


class OpenShiftRequest(BaseModel):
    """Schema para abrir un turno"""

    cashier_name: str = Field(
        ...,
        max_length=128,
        description="Nombre del cajero",
        validation_alias=AliasChoices("cashierName", "cashier_name"),
        serialization_alias="cashierName",
    )
    opening_balance: Decimal = Field(
        ...,
        ge=0,
        description="Balance de apertura",
        validation_alias=AliasChoices("openingBalance", "opening_balance"),
        serialization_alias="openingBalance",
    )
    notes: str | None = Field(None, max_length=512, description="Notas adicionales")


class CloseShiftRequest(BaseModel):
    """Schema para cerrar un turno"""

    closing_balance: Decimal = Field(
        ...,
        ge=0,
        description="Balance de cierre",
        validation_alias=AliasChoices("closingBalance", "closing_balance"),
        serialization_alias="closingBalance",
    )
    notes: str | None = Field(None, max_length=512, description="Notas adicionales")


class ShiftResponse(BaseModel):
    """Schema para respuesta de un turno"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    cashier_name: str = Field(
        ...,
        validation_alias=AliasChoices("cashierName", "cashier_name"),
        serialization_alias="cashierName",
    )
    opened_at: datetime | None = Field(
        None,
        validation_alias=AliasChoices("openedAt", "opened_at"),
        serialization_alias="openedAt",
    )
    closed_at: datetime | None = Field(
        None,
        validation_alias=AliasChoices("closedAt", "closed_at"),
        serialization_alias="closedAt",
    )
    opening_balance: DecimalNumber = Field(
        ...,
        validation_alias=AliasChoices("openingBalance", "opening_balance"),
        serialization_alias="openingBalance",
    )
    closing_balance: DecimalNumber | None = Field(
        None,
        validation_alias=AliasChoices("closingBalance", "closing_balance"),
        serialization_alias="closingBalance",
    )
    expected_balance: DecimalNumber | None = Field(
        None,
        validation_alias=AliasChoices("expectedBalance", "expected_balance"),
        serialization_alias="expectedBalance",
    )
    discrepancy: DecimalNumber | None = Field(
        None,
        validation_alias=AliasChoices("discrepancy"),
    )
    status: str
    notes: str | None = None


class ShiftQueryParams(QueryParams):
    status: str | None = None
