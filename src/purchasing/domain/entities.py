from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from src.shared.domain.entities import Entity
from src.shared.domain.exceptions import DomainError


class PurchaseOrderStatus(StrEnum):
    DRAFT = "draft"
    SENT = "sent"
    PARTIAL = "partial"
    RECEIVED = "received"
    CANCELLED = "cancelled"


@dataclass
class PurchaseOrder(Entity):
    supplier_id: int
    order_number: str
    id: int | None = None
    status: PurchaseOrderStatus = PurchaseOrderStatus.DRAFT
    subtotal: Decimal = Decimal("0.00")
    tax: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")
    notes: str | None = None
    expected_date: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def send(self) -> "PurchaseOrder":
        if self.status != PurchaseOrderStatus.DRAFT:
            raise DomainError(
                f"Cannot send a purchase order with status '{self.status.value}'. Only DRAFT orders can be sent."
            )
        return replace(self, status=PurchaseOrderStatus.SENT)

    def cancel(self) -> "PurchaseOrder":
        if self.status == PurchaseOrderStatus.RECEIVED:
            raise DomainError(
                "Cannot cancel a purchase order that has already been received."
            )
        if self.status == PurchaseOrderStatus.CANCELLED:
            raise DomainError("Purchase order is already cancelled.")
        return replace(self, status=PurchaseOrderStatus.CANCELLED)

    def mark_partial(self) -> "PurchaseOrder":
        return replace(self, status=PurchaseOrderStatus.PARTIAL)

    def mark_received(self) -> "PurchaseOrder":
        return replace(self, status=PurchaseOrderStatus.RECEIVED)


@dataclass
class PurchaseOrderItem(Entity):
    purchase_order_id: int
    product_id: int
    quantity_ordered: int
    unit_cost: Decimal
    id: int | None = None
    quantity_received: int = 0

    @property
    def quantity_pending(self) -> int:
        return self.quantity_ordered - self.quantity_received

    @property
    def subtotal(self) -> Decimal:
        return self.unit_cost * self.quantity_ordered


@dataclass
class PurchaseReceipt(Entity):
    purchase_order_id: int
    id: int | None = None
    notes: str | None = None
    received_at: datetime | None = None
    created_at: datetime | None = None


@dataclass
class PurchaseReceiptItem(Entity):
    purchase_receipt_id: int
    purchase_order_item_id: int
    product_id: int
    quantity_received: int
    id: int | None = None
    location_id: int | None = None
