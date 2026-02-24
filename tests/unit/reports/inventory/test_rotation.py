from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from src.reports.inventory.app.queries.rotation import (
    GetProductRotationQuery,
    GetProductRotationQueryHandler,
)


def _make_session():
    session = MagicMock()
    q = MagicMock()
    q.join.return_value = q
    q.filter.return_value = q
    q.group_by.return_value = q
    q.all.return_value = []
    session.query.return_value = q
    return session


def _make_movement_row(
    product_id=1, product_name="Product A", sku="SKU-001", total_in=100, total_out=80
):
    row = MagicMock()
    row.product_id = product_id
    row.product_name = product_name
    row.sku = sku
    row.total_in = total_in
    row.total_out = total_out
    return row


# ---------------------------------------------------------------------------
# GetProductRotationQueryHandler
# ---------------------------------------------------------------------------


def test_rotation_returns_empty_when_no_movements():
    session = _make_session()
    handler = GetProductRotationQueryHandler(session)

    result = handler.handle(
        GetProductRotationQuery(from_date=date(2026, 1, 1), to_date=date(2026, 1, 31))
    )

    assert result == []


def test_rotation_calculates_turnover_rate():
    handler = GetProductRotationQueryHandler(MagicMock())
    movement_row = _make_movement_row(total_in=100, total_out=80)
    stock_rows = {1: 40}  # current stock

    with (
        patch.object(
            handler, "_fetch_movement_aggregates", return_value=[movement_row]
        ),
        patch.object(handler, "_fetch_current_stocks", return_value=stock_rows),
    ):
        result = handler.handle(
            GetProductRotationQuery(
                from_date=date(2026, 1, 1), to_date=date(2026, 1, 31)
            )
        )

    assert len(result) == 1
    assert result[0]["total_in"] == 100
    assert result[0]["total_out"] == 80
    assert result[0]["current_stock"] == 40
    assert result[0]["turnover_rate"] == Decimal("2")  # 80 / 40


def test_rotation_sets_turnover_zero_when_no_stock():
    handler = GetProductRotationQueryHandler(MagicMock())
    movement_row = _make_movement_row(total_in=50, total_out=30)
    stock_rows = {1: 0}  # no current stock

    with (
        patch.object(
            handler, "_fetch_movement_aggregates", return_value=[movement_row]
        ),
        patch.object(handler, "_fetch_current_stocks", return_value=stock_rows),
    ):
        result = handler.handle(
            GetProductRotationQuery(
                from_date=date(2026, 1, 1), to_date=date(2026, 1, 31)
            )
        )

    assert result[0]["turnover_rate"] == Decimal("0")
    assert result[0]["days_of_stock"] is None


def test_rotation_calculates_days_of_stock():
    handler = GetProductRotationQueryHandler(MagicMock())
    # 31 days period, 310 total_out → 10/day, current_stock=100 → 10 days
    movement_row = _make_movement_row(total_in=400, total_out=310)
    stock_rows = {1: 100}

    with (
        patch.object(
            handler, "_fetch_movement_aggregates", return_value=[movement_row]
        ),
        patch.object(handler, "_fetch_current_stocks", return_value=stock_rows),
    ):
        result = handler.handle(
            GetProductRotationQuery(
                from_date=date(2026, 1, 1), to_date=date(2026, 1, 31)
            )
        )

    assert result[0]["days_of_stock"] == 10


def test_rotation_days_of_stock_none_when_no_out():
    handler = GetProductRotationQueryHandler(MagicMock())
    movement_row = _make_movement_row(total_in=100, total_out=0)
    stock_rows = {1: 50}

    with (
        patch.object(
            handler, "_fetch_movement_aggregates", return_value=[movement_row]
        ),
        patch.object(handler, "_fetch_current_stocks", return_value=stock_rows),
    ):
        result = handler.handle(
            GetProductRotationQuery(
                from_date=date(2026, 1, 1), to_date=date(2026, 1, 31)
            )
        )

    assert result[0]["days_of_stock"] is None


def test_rotation_uses_zero_stock_when_product_not_in_stocks():
    handler = GetProductRotationQueryHandler(MagicMock())
    movement_row = _make_movement_row(product_id=99, total_in=10, total_out=5)
    stock_rows = {}  # no stock for product 99

    with (
        patch.object(
            handler, "_fetch_movement_aggregates", return_value=[movement_row]
        ),
        patch.object(handler, "_fetch_current_stocks", return_value=stock_rows),
    ):
        result = handler.handle(
            GetProductRotationQuery(
                from_date=date(2026, 1, 1), to_date=date(2026, 1, 31)
            )
        )

    assert result[0]["current_stock"] == 0
    assert result[0]["turnover_rate"] == Decimal("0")


def test_rotation_multiple_products():
    handler = GetProductRotationQueryHandler(MagicMock())
    rows = [
        _make_movement_row(
            product_id=1, product_name="P1", sku="S1", total_in=100, total_out=60
        ),
        _make_movement_row(
            product_id=2, product_name="P2", sku="S2", total_in=200, total_out=150
        ),
    ]
    stock_rows = {1: 40, 2: 50}

    with (
        patch.object(handler, "_fetch_movement_aggregates", return_value=rows),
        patch.object(handler, "_fetch_current_stocks", return_value=stock_rows),
    ):
        result = handler.handle(
            GetProductRotationQuery(
                from_date=date(2026, 1, 1), to_date=date(2026, 1, 31)
            )
        )

    assert len(result) == 2
    assert result[0]["product_name"] == "P1"
    assert result[1]["product_name"] == "P2"
