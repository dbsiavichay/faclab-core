from src.purchasing.domain.events import (
    PurchaseOrderCancelled,
    PurchaseOrderCreated,
    PurchaseOrderReceived,
    PurchaseOrderSent,
)


def test_purchase_order_created_payload():
    event = PurchaseOrderCreated(
        aggregate_id=1,
        purchase_order_id=1,
        order_number="PO-2026-0001",
        supplier_id=10,
    )
    payload = event._payload()
    assert payload["purchase_order_id"] == 1
    assert payload["order_number"] == "PO-2026-0001"
    assert payload["supplier_id"] == 10


def test_purchase_order_sent_payload():
    event = PurchaseOrderSent(
        aggregate_id=1,
        purchase_order_id=1,
        order_number="PO-2026-0001",
    )
    payload = event._payload()
    assert payload["purchase_order_id"] == 1
    assert payload["order_number"] == "PO-2026-0001"


def test_purchase_order_received_payload():
    items = [
        {"product_id": 5, "quantity": 10, "location_id": None},
        {"product_id": 6, "quantity": 5, "location_id": 2},
    ]
    event = PurchaseOrderReceived(
        aggregate_id=1,
        purchase_order_id=1,
        order_number="PO-2026-0001",
        is_complete=True,
        items=items,
    )
    payload = event._payload()
    assert payload["purchase_order_id"] == 1
    assert payload["is_complete"] is True
    assert len(payload["items"]) == 2


def test_purchase_order_cancelled_payload():
    event = PurchaseOrderCancelled(
        aggregate_id=1,
        purchase_order_id=1,
        order_number="PO-2026-0001",
    )
    payload = event._payload()
    assert payload["purchase_order_id"] == 1
    assert payload["order_number"] == "PO-2026-0001"
