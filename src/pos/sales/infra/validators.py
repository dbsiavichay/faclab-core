"""Pydantic schemas para validacion POS Sales"""

from decimal import Decimal

from pydantic import AliasChoices, BaseModel, Field


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
