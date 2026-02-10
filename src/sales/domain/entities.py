from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from src.shared.domain.entities import Entity


class SaleStatus(str, Enum):
    """Estado de una venta"""

    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    INVOICED = "INVOICED"
    CANCELLED = "CANCELLED"


class PaymentStatus(str, Enum):
    """Estado de pago de una venta"""

    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    PAID = "PAID"


class PaymentMethod(str, Enum):
    """Método de pago"""

    CASH = "CASH"
    CARD = "CARD"
    TRANSFER = "TRANSFER"
    CREDIT = "CREDIT"


@dataclass
class SaleItem(Entity):
    """Item individual de una venta"""

    sale_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    discount: Decimal = Decimal("0")
    id: Optional[int] = None

    @property
    def subtotal(self) -> Decimal:
        """Calcula el subtotal del item (cantidad * precio - descuento)"""
        base = self.unit_price * self.quantity
        discount_amount = base * (self.discount / Decimal("100"))
        return base - discount_amount


@dataclass
class Sale(Entity):
    """Venta del sistema"""

    customer_id: int
    status: SaleStatus = SaleStatus.DRAFT
    sale_date: Optional[datetime] = None
    subtotal: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    discount: Decimal = Decimal("0")
    total: Decimal = Decimal("0")
    payment_status: PaymentStatus = PaymentStatus.PENDING
    notes: Optional[str] = None
    created_by: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def confirm(self) -> None:
        """Confirma la venta (solo si está en DRAFT)"""
        if self.status != SaleStatus.DRAFT:
            raise ValueError(
                f"Only DRAFT sales can be confirmed. Current status: {self.status}"
            )
        self.status = SaleStatus.CONFIRMED
        if self.sale_date is None:
            self.sale_date = datetime.now()

    def cancel(self) -> None:
        """Cancela la venta (solo si está en DRAFT o CONFIRMED)"""
        if self.status not in (SaleStatus.DRAFT, SaleStatus.CONFIRMED):
            raise ValueError(
                f"Only DRAFT or CONFIRMED sales can be cancelled. "
                f"Current status: {self.status}"
            )
        self.status = SaleStatus.CANCELLED

    def invoice(self) -> None:
        """Marca la venta como facturada (solo si está CONFIRMED)"""
        if self.status != SaleStatus.CONFIRMED:
            raise ValueError(
                f"Only CONFIRMED sales can be invoiced. Current status: {self.status}"
            )
        self.status = SaleStatus.INVOICED

    def update_payment_status(self, total_paid: Decimal) -> None:
        """Actualiza el estado de pago basándose en el monto pagado"""
        if total_paid <= Decimal("0"):
            self.payment_status = PaymentStatus.PENDING
        elif total_paid >= self.total:
            self.payment_status = PaymentStatus.PAID
        else:
            self.payment_status = PaymentStatus.PARTIAL


@dataclass
class Payment(Entity):
    """Pago realizado para una venta"""

    sale_id: int
    amount: Decimal
    payment_method: PaymentMethod
    payment_date: Optional[datetime] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Valida que el monto sea positivo"""
        if self.amount <= Decimal("0"):
            raise ValueError(f"Payment amount must be positive, got {self.amount}")
        if self.payment_date is None:
            self.payment_date = datetime.now()
