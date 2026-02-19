"""Pydantic schemas para validación y serialización de Sales"""

from datetime import datetime
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class SaleItemRequest(BaseModel):
    """Schema para input de un item de venta"""

    product_id: int = Field(
        ...,
        gt=0,
        description="ID del producto",
        validation_alias=AliasChoices("productId", "product_id"),
        serialization_alias="productId",
    )
    quantity: int = Field(..., gt=0, description="Cantidad del producto")
    unit_price: float = Field(
        ...,
        gt=0,
        description="Precio unitario",
        validation_alias=AliasChoices("unitPrice", "unit_price"),
        serialization_alias="unitPrice",
    )
    discount: float = Field(0.0, ge=0, le=100, description="Porcentaje de descuento")


class SaleRequest(BaseModel):
    """Schema para crear una venta"""

    customer_id: int = Field(
        ...,
        gt=0,
        description="ID del cliente",
        validation_alias=AliasChoices("customerId", "customer_id"),
        serialization_alias="customerId",
    )
    notes: str | None = Field(None, max_length=512, description="Notas adicionales")
    created_by: str | None = Field(
        None,
        max_length=64,
        description="Usuario que crea",
        validation_alias=AliasChoices("createdBy", "created_by"),
        serialization_alias="createdBy",
    )


class PaymentRequest(BaseModel):
    """Schema para registrar un pago"""

    amount: float = Field(..., gt=0, description="Monto del pago")
    payment_method: str = Field(
        ...,
        description="Método de pago",
        validation_alias=AliasChoices("paymentMethod", "payment_method"),
        serialization_alias="paymentMethod",
    )
    reference: str | None = Field(
        None, max_length=128, description="Referencia del pago"
    )
    notes: str | None = Field(None, max_length=512, description="Notas del pago")


class CancelSaleRequest(BaseModel):
    """Schema para cancelar una venta"""

    reason: str | None = Field(
        None, max_length=512, description="Razón de la cancelación"
    )


class SaleItemResponse(BaseModel):
    """Schema para respuesta de un item de venta"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sale_id: int = Field(
        ...,
        validation_alias=AliasChoices("saleId", "sale_id"),
        serialization_alias="saleId",
    )
    product_id: int = Field(
        ...,
        validation_alias=AliasChoices("productId", "product_id"),
        serialization_alias="productId",
    )
    quantity: int
    unit_price: Decimal = Field(
        ...,
        validation_alias=AliasChoices("unitPrice", "unit_price"),
        serialization_alias="unitPrice",
    )
    discount: Decimal
    subtotal: Decimal


class PaymentResponse(BaseModel):
    """Schema para respuesta de un pago"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sale_id: int = Field(
        ...,
        validation_alias=AliasChoices("saleId", "sale_id"),
        serialization_alias="saleId",
    )
    amount: Decimal
    payment_method: str = Field(
        ...,
        validation_alias=AliasChoices("paymentMethod", "payment_method"),
        serialization_alias="paymentMethod",
    )
    payment_date: datetime | None = Field(
        None,
        validation_alias=AliasChoices("paymentDate", "payment_date"),
        serialization_alias="paymentDate",
    )
    reference: str | None
    notes: str | None
    created_at: datetime | None = Field(
        None,
        validation_alias=AliasChoices("createdAt", "created_at"),
        serialization_alias="createdAt",
    )


class SaleResponse(BaseModel):
    """Schema para respuesta de una venta"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int = Field(
        ...,
        validation_alias=AliasChoices("customerId", "customer_id"),
        serialization_alias="customerId",
    )
    status: str
    sale_date: datetime | None = Field(
        None,
        validation_alias=AliasChoices("saleDate", "sale_date"),
        serialization_alias="saleDate",
    )
    subtotal: Decimal
    tax: Decimal
    discount: Decimal
    total: Decimal
    payment_status: str = Field(
        ...,
        validation_alias=AliasChoices("paymentStatus", "payment_status"),
        serialization_alias="paymentStatus",
    )
    notes: str | None
    created_by: str | None = Field(
        None,
        validation_alias=AliasChoices("createdBy", "created_by"),
        serialization_alias="createdBy",
    )
    created_at: datetime | None = Field(
        None,
        validation_alias=AliasChoices("createdAt", "created_at"),
        serialization_alias="createdAt",
    )
    updated_at: datetime | None = Field(
        None,
        validation_alias=AliasChoices("updatedAt", "updated_at"),
        serialization_alias="updatedAt",
    )


class SaleDetailResponse(SaleResponse):
    """Schema para respuesta de una venta con items y pagos"""

    model_config = ConfigDict(from_attributes=True)

    items: list[SaleItemResponse] = []
    payments: list[PaymentResponse] = []
