"""TypedDicts para input/output de comandos y queries"""

from typing import Optional, TypedDict


class SaleInput(TypedDict, total=False):
    """Input para crear una venta"""

    customer_id: int
    notes: Optional[str]
    created_by: Optional[str]


class SaleItemInput(TypedDict, total=False):
    """Input para agregar un item a una venta"""

    sale_id: int
    product_id: int
    quantity: int
    unit_price: float
    discount: Optional[float]


class PaymentInput(TypedDict, total=False):
    """Input para registrar un pago"""

    sale_id: int
    amount: float
    payment_method: str
    reference: Optional[str]
    notes: Optional[str]


class SaleOutput(TypedDict, total=False):
    """Output de una venta"""

    id: int
    customer_id: int
    status: str
    sale_date: Optional[str]
    subtotal: float
    tax: float
    discount: float
    total: float
    payment_status: str
    notes: Optional[str]
    created_by: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


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
    payment_date: Optional[str]
    reference: Optional[str]
    notes: Optional[str]
    created_at: Optional[str]
