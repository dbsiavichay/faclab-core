from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.shared.infra.validators import DecimalNumber, QueryParams


class RegisterCashMovementRequest(BaseModel):
    type: str = Field(..., pattern="^(IN|OUT)$", description="IN or OUT")
    amount: DecimalNumber = Field(..., gt=0)
    reason: str | None = Field(None, max_length=512)
    performed_by: str | None = Field(
        None,
        max_length=64,
        validation_alias=AliasChoices("performedBy", "performed_by"),
        serialization_alias="performedBy",
    )


class CashMovementResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    shift_id: int
    type: str
    amount: DecimalNumber
    reason: str | None = None
    performed_by: str | None = None
    created_at: datetime | None = None


class CashMovementQueryParams(QueryParams):
    pass


class CashSummaryResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    shift_id: int
    opening_balance: DecimalNumber
    cash_sales: DecimalNumber
    cash_refunds: DecimalNumber
    cash_in: DecimalNumber
    cash_out: DecimalNumber
    expected_balance: DecimalNumber
