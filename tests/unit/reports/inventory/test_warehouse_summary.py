from decimal import Decimal
from unittest.mock import MagicMock

from src.reports.inventory.app.queries.warehouse_summary import (
    GetWarehouseSummaryQuery,
    GetWarehouseSummaryQueryHandler,
)


def _make_session(rows=None):
    rows = rows or []
    session = MagicMock()
    q = MagicMock()
    q.join.return_value = q
    q.filter.return_value = q
    q.group_by.return_value = q
    q.all.return_value = rows
    session.query.return_value = q
    return session


def _make_row(
    id=1,
    name="Main Warehouse",
    code="WH-01",
    total_products=10,
    total_quantity=500,
    reserved_quantity=50,
    total_value=Decimal("5000.00"),
):
    row = MagicMock()
    row.id = id
    row.name = name
    row.code = code
    row.total_products = total_products
    row.total_quantity = total_quantity
    row.reserved_quantity = reserved_quantity
    row.total_value = total_value
    return row


# ---------------------------------------------------------------------------
# GetWarehouseSummaryQueryHandler
# ---------------------------------------------------------------------------


def test_summary_returns_empty_when_no_warehouses():
    session = _make_session(rows=[])
    handler = GetWarehouseSummaryQueryHandler(session)

    result = handler.handle(GetWarehouseSummaryQuery())

    assert result == []


def test_summary_returns_correct_warehouse_fields():
    row = _make_row(
        id=1,
        name="Main Warehouse",
        code="WH-01",
        total_products=5,
        total_quantity=100,
        reserved_quantity=20,
        total_value=Decimal("1000.00"),
    )
    session = _make_session(rows=[row])
    handler = GetWarehouseSummaryQueryHandler(session)

    result = handler.handle(GetWarehouseSummaryQuery())

    assert len(result) == 1
    item = result[0]
    assert item["warehouse_id"] == 1
    assert item["warehouse_name"] == "Main Warehouse"
    assert item["warehouse_code"] == "WH-01"
    assert item["total_products"] == 5
    assert item["total_quantity"] == 100
    assert item["reserved_quantity"] == 20
    assert item["total_value"] == Decimal("1000.00")


def test_summary_calculates_available_quantity():
    row = _make_row(total_quantity=200, reserved_quantity=30)
    session = _make_session(rows=[row])
    handler = GetWarehouseSummaryQueryHandler(session)

    result = handler.handle(GetWarehouseSummaryQuery())

    assert result[0]["available_quantity"] == 170


def test_summary_handles_zero_reserved():
    row = _make_row(total_quantity=100, reserved_quantity=0)
    session = _make_session(rows=[row])
    handler = GetWarehouseSummaryQueryHandler(session)

    result = handler.handle(GetWarehouseSummaryQuery())

    assert result[0]["available_quantity"] == 100


def test_summary_handles_null_total_value():
    row = _make_row(total_value=None)
    session = _make_session(rows=[row])
    handler = GetWarehouseSummaryQueryHandler(session)

    result = handler.handle(GetWarehouseSummaryQuery())

    assert result[0]["total_value"] == Decimal("0")


def test_summary_handles_null_quantities():
    row = _make_row(total_quantity=None, reserved_quantity=None, total_products=None)
    session = _make_session(rows=[row])
    handler = GetWarehouseSummaryQueryHandler(session)

    result = handler.handle(GetWarehouseSummaryQuery())

    item = result[0]
    assert item["total_quantity"] == 0
    assert item["reserved_quantity"] == 0
    assert item["total_products"] == 0
    assert item["available_quantity"] == 0


def test_summary_multiple_warehouses():
    rows = [
        _make_row(
            id=1, name="WH A", code="WH-A", total_quantity=100, reserved_quantity=10
        ),
        _make_row(
            id=2, name="WH B", code="WH-B", total_quantity=200, reserved_quantity=5
        ),
    ]
    session = _make_session(rows=rows)
    handler = GetWarehouseSummaryQueryHandler(session)

    result = handler.handle(GetWarehouseSummaryQuery())

    assert len(result) == 2
    assert result[0]["warehouse_code"] == "WH-A"
    assert result[1]["warehouse_code"] == "WH-B"


def test_summary_with_warehouse_id_filter():
    session = _make_session(rows=[])
    handler = GetWarehouseSummaryQueryHandler(session)

    result = handler.handle(GetWarehouseSummaryQuery(warehouse_id=3))

    assert result == []
    assert session.query.called
