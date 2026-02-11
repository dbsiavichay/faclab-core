"""TypedDicts para input/output de comandos y queries"""

from typing import TypedDict


class SaleInput(TypedDict, total=False):
    """Input para crear una venta"""

    customer_id: int
    notes: str | None
    created_by: str | None


class SaleItemInput(TypedDict, total=False):
    """Input para agregar un item a una venta"""

    sale_id: int
    product_id: int
    quantity: int
    unit_price: float
    discount: float | None


class PaymentInput(TypedDict, total=False):
    """Input para registrar un pago"""

    sale_id: int
    amount: float
    payment_method: str
    reference: str | None
    notes: str | None


class SaleOutput(TypedDict, total=False):
    """Output de una venta"""

    id: int
    customer_id: int
    status: str
    sale_date: str | None
    subtotal: float
    tax: float
    discount: float
    total: float
    payment_status: str
    notes: str | None
    created_by: str | None
    created_at: str | None
    updated_at: str | None


class SaleItemOutput(TypedDict, total=False):
    """Output de un item de venta"""

    id: int
    sale_id: int
    product_id: int
    quantity: int
    unit_price: float
    discount: float
    subtotal: float


class PaymentOutput(TypedDict, total=False):
    """Output de un pago"""

    id: int
    sale_id: int
    amount: float
    payment_method: str
    payment_date: str | None
    reference: str | None
    notes: str | None
    created_at: str | None
