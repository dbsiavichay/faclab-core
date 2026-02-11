"""Pydantic schemas para validación y serialización de Sales"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class SaleItemInput(BaseModel):
    """Schema para input de un item de venta"""

    product_id: int = Field(..., gt=0, description="ID del producto")
    quantity: int = Field(..., gt=0, description="Cantidad del producto")
    unit_price: float = Field(..., gt=0, description="Precio unitario")
    discount: float = Field(0.0, ge=0, le=100, description="Porcentaje de descuento")


class SaleInput(BaseModel):
    """Schema para crear una venta"""

    customer_id: int = Field(..., gt=0, description="ID del cliente")
    notes: str | None = Field(None, max_length=512, description="Notas adicionales")
    created_by: str | None = Field(
        None, max_length=64, description="Usuario que crea"
    )


class PaymentInput(BaseModel):
    """Schema para registrar un pago"""

    amount: float = Field(..., gt=0, description="Monto del pago")
    payment_method: str = Field(..., description="Método de pago")
    reference: str | None = Field(
        None, max_length=128, description="Referencia del pago"
    )
    notes: str | None = Field(None, max_length=512, description="Notas del pago")


class CancelSaleInput(BaseModel):
    """Schema para cancelar una venta"""

    reason: str | None = Field(
        None, max_length=512, description="Razón de la cancelación"
    )


class SaleItemResponse(BaseModel):
    """Schema para respuesta de un item de venta"""

    id: int
    sale_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    discount: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    """Schema para respuesta de un pago"""

    id: int
    sale_id: int
    amount: Decimal
    payment_method: str
    payment_date: datetime | None
    reference: str | None
    notes: str | None
    created_at: datetime | None

    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    """Schema para respuesta de una venta"""

    id: int
    customer_id: int
    status: str
    sale_date: datetime | None
    subtotal: Decimal
    tax: Decimal
    discount: Decimal
    total: Decimal
    payment_status: str
    notes: str | None
    created_by: str | None
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = True


class SaleDetailResponse(SaleResponse):
    """Schema para respuesta de una venta con items y pagos"""

    items: list[SaleItemResponse] = []
    payments: list[PaymentResponse] = []

    class Config:
        from_attributes = True
