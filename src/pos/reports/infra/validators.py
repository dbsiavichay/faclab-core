import datetime as dt

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.shared.infra.validators import DecimalNumber

# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------


class PaymentMethodDetail(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    payment_method: str
    count: int
    total: DecimalNumber


class ItemSoldDetail(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    product_name: str
    sku: str
    quantity: int
    total: DecimalNumber


class ShiftInfo(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    cashier_name: str
    opened_at: str | None = None
    status: str


class SalesSummary(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    count: int
    subtotal: DecimalNumber
    tax: DecimalNumber
    discount: DecimalNumber
    total: DecimalNumber


class RefundSummary(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    count: int
    total: DecimalNumber


class CashReconciliation(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    opening_balance: DecimalNumber
    cash_sales: DecimalNumber
    cash_refunds: DecimalNumber
    cash_in: DecimalNumber
    cash_out: DecimalNumber
    expected_balance: DecimalNumber
    closing_balance: DecimalNumber | None = None
    discrepancy: DecimalNumber | None = None


# ---------------------------------------------------------------------------
# X-Report
# ---------------------------------------------------------------------------


class XReportResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    shift: ShiftInfo
    sales_summary: SalesSummary
    payments_by_method: list[PaymentMethodDetail]
    items_sold: list[ItemSoldDetail]


class XReportQueryParams(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    shift_id: int = Field(..., ge=1)


# ---------------------------------------------------------------------------
# Z-Report
# ---------------------------------------------------------------------------


class ZReportResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    shift: ShiftInfo
    sales_summary: SalesSummary
    payments_by_method: list[PaymentMethodDetail]
    items_sold: list[ItemSoldDetail]
    refund_summary: RefundSummary
    cash_reconciliation: CashReconciliation


class ZReportQueryParams(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    shift_id: int = Field(..., ge=1)


# ---------------------------------------------------------------------------
# Daily Summary
# ---------------------------------------------------------------------------


class DailySummaryResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    date: str
    total_sales: int
    total_amount: DecimalNumber
    payments_by_method: list[PaymentMethodDetail]
    top_products: list[ItemSoldDetail]
    refund_summary: RefundSummary


class DailySummaryQueryParams(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    date: dt.date = Field(default_factory=dt.date.today)


# ---------------------------------------------------------------------------
# By Payment Method
# ---------------------------------------------------------------------------


class PaymentMethodSummaryResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    payment_method: str
    sales_count: int
    total_amount: DecimalNumber


class ByPaymentMethodQueryParams(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    from_date: dt.date | None = None
    to_date: dt.date | None = None
