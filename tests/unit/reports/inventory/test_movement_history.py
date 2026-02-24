from datetime import date, datetime
from unittest.mock import MagicMock

from src.reports.inventory.app.queries.movement_history import (
    GetMovementHistoryReportQuery,
    GetMovementHistoryReportQueryHandler,
)


def _make_session(rows=None, count=None):
    """Return a mock Session where the query chain returns specific rows."""
    rows = rows or []
    count = count if count is not None else len(rows)
    session = MagicMock()
    q = MagicMock()
    q.join.return_value = q
    q.filter.return_value = q
    q.order_by.return_value = q
    q.offset.return_value = q
    q.limit.return_value = q
    q.count.return_value = count
    q.all.return_value = rows
    session.query.return_value = q
    return session


def _make_row(
    id=1,
    product_id=1,
    product_name="Product A",
    sku="SKU-001",
    quantity=10,
    type="in",
    location_id=None,
    source_location_id=None,
    reference_type=None,
    reference_id=None,
    reason=None,
    date_val=None,
    created_at=None,
):
    row = MagicMock()
    row.id = id
    row.product_id = product_id
    row.product_name = product_name
    row.sku = sku
    row.quantity = quantity
    row.type = type
    row.location_id = location_id
    row.source_location_id = source_location_id
    row.reference_type = reference_type
    row.reference_id = reference_id
    row.reason = reason
    row.date = date_val or datetime(2026, 2, 1, 10, 0)
    row.created_at = created_at or datetime(2026, 2, 1, 10, 0)
    return row


# ---------------------------------------------------------------------------
# GetMovementHistoryReportQueryHandler
# ---------------------------------------------------------------------------


def test_movement_history_returns_paginated_structure():
    rows = [_make_row(id=1), _make_row(id=2)]
    session = _make_session(rows=rows, count=5)
    handler = GetMovementHistoryReportQueryHandler(session)

    result = handler.handle(GetMovementHistoryReportQuery(limit=2, offset=0))

    assert result["total"] == 5
    assert result["limit"] == 2
    assert result["offset"] == 0
    assert len(result["items"]) == 2


def test_movement_history_returns_empty_when_no_movements():
    session = _make_session(rows=[], count=0)
    handler = GetMovementHistoryReportQueryHandler(session)

    result = handler.handle(GetMovementHistoryReportQuery())

    assert result["total"] == 0
    assert result["items"] == []


def test_movement_history_item_includes_product_name_and_sku():
    row = _make_row(
        product_id=42,
        product_name="Coffee Beans",
        sku="COFFEE-001",
        quantity=25,
        type="in",
    )
    session = _make_session(rows=[row])
    handler = GetMovementHistoryReportQueryHandler(session)

    result = handler.handle(GetMovementHistoryReportQuery())

    item = result["items"][0]
    assert item["product_id"] == 42
    assert item["product_name"] == "Coffee Beans"
    assert item["sku"] == "COFFEE-001"
    assert item["quantity"] == 25
    assert item["type"] == "in"


def test_movement_history_includes_reference_fields():
    row = _make_row(
        reference_type="purchase_order",
        reference_id=7,
        reason="Goods received",
    )
    session = _make_session(rows=[row])
    handler = GetMovementHistoryReportQueryHandler(session)

    result = handler.handle(GetMovementHistoryReportQuery())

    item = result["items"][0]
    assert item["reference_type"] == "purchase_order"
    assert item["reference_id"] == 7
    assert item["reason"] == "Goods received"


def test_movement_history_default_limit_is_50():
    session = _make_session()
    handler = GetMovementHistoryReportQueryHandler(session)

    result = handler.handle(GetMovementHistoryReportQuery())

    assert result["limit"] == 50


def test_movement_history_respects_offset_and_limit():
    session = _make_session(rows=[], count=100)
    handler = GetMovementHistoryReportQueryHandler(session)

    result = handler.handle(GetMovementHistoryReportQuery(limit=10, offset=20))

    assert result["limit"] == 10
    assert result["offset"] == 20


def test_movement_history_applies_product_id_filter():
    session = _make_session(rows=[])
    handler = GetMovementHistoryReportQueryHandler(session)

    handler.handle(GetMovementHistoryReportQuery(product_id=5))

    # Query was called once
    assert session.query.called


def test_movement_history_applies_date_filters():
    session = _make_session(rows=[])
    handler = GetMovementHistoryReportQueryHandler(session)

    handler.handle(
        GetMovementHistoryReportQuery(
            from_date=date(2026, 1, 1),
            to_date=date(2026, 1, 31),
        )
    )

    assert session.query.called


def test_movement_history_nullable_fields_preserved():
    row = _make_row(location_id=None, source_location_id=None, reference_type=None)
    session = _make_session(rows=[row])
    handler = GetMovementHistoryReportQueryHandler(session)

    result = handler.handle(GetMovementHistoryReportQuery())

    item = result["items"][0]
    assert item["location_id"] is None
    assert item["source_location_id"] is None
    assert item["reference_type"] is None
