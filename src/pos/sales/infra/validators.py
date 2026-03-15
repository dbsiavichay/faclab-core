"""Pydantic schemas para validacion POS Sales"""

from datetime import datetime
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from src.shared.infra.validators import DecimalNumber


class ParkSaleRequest(BaseModel):
    """Schema para aparcar una venta"""

    reason: str | None = Field(
        None, max_length=512, description="Razon para aparcar la venta"
    )


class ApplyDiscountRequest(BaseModel):
    """Schema para aplicar descuento a una venta"""

    discount_type: str = Field(
        ...,
        description="Tipo de descuento: PERCENTAGE o AMOUNT",
        validation_alias=AliasChoices("discountType", "discount_type"),
        serialization_alias="discountType",
    )
    discount_value: Decimal = Field(
        ...,
        ge=0,
        description="Valor del descuento",
        validation_alias=AliasChoices("discountValue", "discount_value"),
        serialization_alias="discountValue",
    )


class OverridePriceRequest(BaseModel):
    """Schema para sobreescribir el precio de un item"""

    new_price: Decimal = Field(
        ...,
        gt=0,
        validation_alias=AliasChoices("newPrice", "new_price"),
        serialization_alias="newPrice",
    )
    reason: str = Field(..., min_length=1, max_length=512)


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


class QuickSaleItemInput(BaseModel):
    """Schema para un item de venta rapida"""

    product_id: int = Field(
        ...,
        gt=0,
        description="ID del producto",
        validation_alias=AliasChoices("productId", "product_id"),
        serialization_alias="productId",
    )
    quantity: int = Field(..., gt=0, description="Cantidad")
    unit_price: Decimal | None = Field(
        None,
        gt=0,
        description="Precio unitario (si no se envia, usa el precio del producto)",
        validation_alias=AliasChoices("unitPrice", "unit_price"),
        serialization_alias="unitPrice",
    )
    discount: Decimal = Field(
        Decimal("0"), ge=0, le=100, description="Porcentaje de descuento"
    )


class QuickSalePaymentInput(BaseModel):
    """Schema para un pago de venta rapida"""

    amount: Decimal = Field(..., gt=0, description="Monto del pago")
    payment_method: str = Field(
        ...,
        description="Metodo de pago",
        validation_alias=AliasChoices("paymentMethod", "payment_method"),
        serialization_alias="paymentMethod",
    )
    reference: str | None = Field(
        None, max_length=128, description="Referencia del pago"
    )


class QuickSaleRequest(BaseModel):
    """Schema para venta rapida (checkout completo en un request)"""

    customer_id: int | None = Field(
        None,
        gt=0,
        description="ID del cliente (si no se envia, es consumidor final)",
        validation_alias=AliasChoices("customerId", "customer_id"),
        serialization_alias="customerId",
    )
    items: list[QuickSaleItemInput] = Field(
        ..., min_length=1, description="Items de la venta"
    )
    payments: list[QuickSalePaymentInput] = Field(
        ..., min_length=1, description="Pagos de la venta"
    )
    notes: str | None = Field(None, max_length=512, description="Notas adicionales")
    created_by: str | None = Field(
        None,
        max_length=64,
        description="Usuario que crea",
        validation_alias=AliasChoices("createdBy", "created_by"),
        serialization_alias="createdBy",
    )


class ReceiptItemResponse(BaseModel):
    """Schema para un item del recibo"""

    model_config = ConfigDict(from_attributes=True)

    product_name: str = Field(
        ...,
        validation_alias=AliasChoices("productName", "product_name"),
        serialization_alias="productName",
    )
    quantity: int
    unit_price: DecimalNumber = Field(
        ...,
        validation_alias=AliasChoices("unitPrice", "unit_price"),
        serialization_alias="unitPrice",
    )
    discount: DecimalNumber
    discount_amount: DecimalNumber = Field(
        ...,
        validation_alias=AliasChoices("discountAmount", "discount_amount"),
        serialization_alias="discountAmount",
    )
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
    price_override: DecimalNumber | None = Field(
        None,
        validation_alias=AliasChoices("priceOverride", "price_override"),
        serialization_alias="priceOverride",
    )
    override_reason: str | None = Field(
        None,
        validation_alias=AliasChoices("overrideReason", "override_reason"),
        serialization_alias="overrideReason",
    )


class TaxBreakdownResponse(BaseModel):
    """Schema para desglose de impuestos"""

    model_config = ConfigDict(from_attributes=True)

    tax_rate: DecimalNumber = Field(
        ...,
        validation_alias=AliasChoices("taxRate", "tax_rate"),
        serialization_alias="taxRate",
    )
    taxable_base: DecimalNumber = Field(
        ...,
        validation_alias=AliasChoices("taxableBase", "taxable_base"),
        serialization_alias="taxableBase",
    )
    tax_amount: DecimalNumber = Field(
        ...,
        validation_alias=AliasChoices("taxAmount", "tax_amount"),
        serialization_alias="taxAmount",
    )


class ReceiptPaymentResponse(BaseModel):
    """Schema para un pago del recibo"""

    model_config = ConfigDict(from_attributes=True)

    method: str
    amount: DecimalNumber
    reference: str | None = None


class CustomerReceiptResponse(BaseModel):
    """Schema para datos del cliente en el recibo"""

    model_config = ConfigDict(from_attributes=True)

    name: str
    tax_id: str = Field(
        ...,
        validation_alias=AliasChoices("taxId", "tax_id"),
        serialization_alias="taxId",
    )
    address: str | None = None


class ReceiptResponse(BaseModel):
    """Schema para respuesta del recibo completo"""

    model_config = ConfigDict(from_attributes=True)

    sale_id: int = Field(
        ...,
        validation_alias=AliasChoices("saleId", "sale_id"),
        serialization_alias="saleId",
    )
    sale_date: datetime | None = Field(
        None,
        validation_alias=AliasChoices("saleDate", "sale_date"),
        serialization_alias="saleDate",
    )
    status: str
    cashier: str | None = None
    customer: CustomerReceiptResponse | None = None
    is_final_consumer: bool = Field(
        ...,
        validation_alias=AliasChoices("isFinalConsumer", "is_final_consumer"),
        serialization_alias="isFinalConsumer",
    )
    items: list[ReceiptItemResponse]
    tax_breakdown: list[TaxBreakdownResponse] = Field(
        ...,
        validation_alias=AliasChoices("taxBreakdown", "tax_breakdown"),
        serialization_alias="taxBreakdown",
    )
    subtotal: DecimalNumber
    discount: DecimalNumber
    discount_type: str | None = Field(
        None,
        validation_alias=AliasChoices("discountType", "discount_type"),
        serialization_alias="discountType",
    )
    discount_value: DecimalNumber = Field(
        ...,
        validation_alias=AliasChoices("discountValue", "discount_value"),
        serialization_alias="discountValue",
    )
    tax: DecimalNumber
    total: DecimalNumber
    payments: list[ReceiptPaymentResponse]
    total_paid: DecimalNumber = Field(
        ...,
        validation_alias=AliasChoices("totalPaid", "total_paid"),
        serialization_alias="totalPaid",
    )
    change: DecimalNumber
