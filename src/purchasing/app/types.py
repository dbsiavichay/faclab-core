from decimal import Decimal
from typing import TypedDict


class PurchaseOrderItemData(TypedDict, total=False):
    id: int | None
    purchase_order_id: int
    product_id: int
    quantity_ordered: int
    quantity_received: int
    unit_cost: Decimal
    quantity_pending: int
    subtotal: Decimal


class PurchaseOrderData(TypedDict, total=False):
    id: int | None
    supplier_id: int
    order_number: str
    status: str
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    notes: str | None
    expected_date: str | None
    created_at: str | None
    updated_at: str | None


class PurchaseReceiptItemData(TypedDict, total=False):
    id: int | None
    purchase_receipt_id: int
    purchase_order_item_id: int
    product_id: int
    quantity_received: int
    location_id: int | None


class PurchaseReceiptData(TypedDict, total=False):
    id: int | None
    purchase_order_id: int
    notes: str | None
    received_at: str | None
    created_at: str | None


class ReceiveItemInput(TypedDict):
    purchase_order_item_id: int
    quantity_received: int
    location_id: int | None
