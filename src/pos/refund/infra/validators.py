from datetime import datetime
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from src.shared.infra.validators import DecimalNumber, QueryParams


class CreateRefundItemInput(BaseModel):
    sale_item_id: int = Field(
        ...,
        gt=0,
        description="ID del item de venta original",
        validation_alias=AliasChoices("saleItemId", "sale_item_id"),
        serialization_alias="saleItemId",
    )
    quantity: int = Field(..., gt=0, description="Cantidad a devolver")


class CreateRefundRequest(BaseModel):
    original_sale_id: int = Field(
        ...,
        gt=0,
        description="ID de la venta original",
        validation_alias=AliasChoices("originalSaleId", "original_sale_id"),
        serialization_alias="originalSaleId",
    )
    items: list[CreateRefundItemInput] = Field(
        ..., min_length=1, description="Items a devolver"
    )
    reason: str | None = Field(
        None, max_length=512, description="Razon de la devolucion"
    )
    refunded_by: str | None = Field(
        None,
        max_length=64,
        description="Usuario que realiza la devolucion",
        validation_alias=AliasChoices("refundedBy", "refunded_by"),
        serialization_alias="refundedBy",
    )


class ProcessRefundPaymentInput(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Monto del reembolso")
    payment_method: str = Field(
        ...,
        description="Metodo de pago",
        validation_alias=AliasChoices("paymentMethod", "payment_method"),
        serialization_alias="paymentMethod",
    )
    reference: str | None = Field(
        None, max_length=128, description="Referencia del pago"
    )


class ProcessRefundRequest(BaseModel):
    payments: list[ProcessRefundPaymentInput] = Field(
        ..., min_length=1, description="Pagos del reembolso"
    )


class RefundItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    refund_id: int = Field(
        ...,
        validation_alias=AliasChoices("refundId", "refund_id"),
        serialization_alias="refundId",
    )
    original_sale_item_id: int = Field(
        ...,
        validation_alias=AliasChoices("originalSaleItemId", "original_sale_item_id"),
        serialization_alias="originalSaleItemId",
    )
    product_id: int = Field(
        ...,
        validation_alias=AliasChoices("productId", "product_id"),
        serialization_alias="productId",
    )
    quantity: int
    unit_price: DecimalNumber = Field(
        ...,
        validation_alias=AliasChoices("unitPrice", "unit_price"),
        serialization_alias="unitPrice",
    )
    discount: DecimalNumber
    tax_rate: DecimalNumber = Field(
        ...,
        validation_alias=AliasChoices("taxRate", "tax_rate"),
        serialization_alias="taxRate",
    )
    tax_amount: DecimalNumber = Field(
        ...,
        validation_alias=AliasChoices("taxAmount", "tax_amount"),
        serialization_alias="taxAmount",
    )
    subtotal: DecimalNumber


class RefundPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    refund_id: int = Field(
        ...,
        validation_alias=AliasChoices("refundId", "refund_id"),
        serialization_alias="refundId",
    )
    amount: DecimalNumber
    payment_method: str = Field(
        ...,
        validation_alias=AliasChoices("paymentMethod", "payment_method"),
        serialization_alias="paymentMethod",
    )
    reference: str | None
    created_at: datetime | None = Field(
        None,
        validation_alias=AliasChoices("createdAt", "created_at"),
        serialization_alias="createdAt",
    )


class RefundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_sale_id: int = Field(
        ...,
        validation_alias=AliasChoices("originalSaleId", "original_sale_id"),
        serialization_alias="originalSaleId",
    )
    shift_id: int | None = Field(
        None,
        validation_alias=AliasChoices("shiftId", "shift_id"),
        serialization_alias="shiftId",
    )
    refund_date: datetime | None = Field(
        None,
        validation_alias=AliasChoices("refundDate", "refund_date"),
        serialization_alias="refundDate",
    )
    subtotal: DecimalNumber
    tax: DecimalNumber
    total: DecimalNumber
    reason: str | None
    status: str
    refunded_by: str | None = Field(
        None,
        validation_alias=AliasChoices("refundedBy", "refunded_by"),
        serialization_alias="refundedBy",
    )
    created_at: datetime | None = Field(
        None,
        validation_alias=AliasChoices("createdAt", "created_at"),
        serialization_alias="createdAt",
    )


class RefundDetailResponse(RefundResponse):
    model_config = ConfigDict(from_attributes=True)

    items: list[RefundItemResponse] = []
    payments: list[RefundPaymentResponse] = []


class RefundQueryParams(QueryParams):
    sale_id: int | None = Field(None, ge=1)
    status: str | None = None
