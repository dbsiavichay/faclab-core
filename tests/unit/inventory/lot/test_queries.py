from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from src.inventory.lot.app.queries.lot import (
    GetAllLotsQuery,
    GetAllLotsQueryHandler,
    GetExpiringLotsQuery,
    GetExpiringLotsQueryHandler,
    GetLotByIdQuery,
    GetLotByIdQueryHandler,
    GetLotsByProductQuery,
    GetLotsByProductQueryHandler,
)
from src.inventory.lot.domain.entities import Lot
from src.shared.domain.exceptions import NotFoundError


def _make_lot(**overrides) -> Lot:
    defaults = {
        "id": 1,
        "product_id": 5,
        "lot_number": "LOT-001",
        "initial_quantity": 100,
        "current_quantity": 80,
    }
    defaults.update(overrides)
    return Lot(**defaults)


# ---------------------------------------------------------------------------
# GetAllLotsQueryHandler
# ---------------------------------------------------------------------------


def test_get_all_lots():
    lot1 = _make_lot(id=1, lot_number="LOT-001")
    lot2 = _make_lot(id=2, lot_number="LOT-002")
    repo = MagicMock()
    repo.get_all.return_value = [lot1, lot2]
    handler = GetAllLotsQueryHandler(repo)

    result = handler.handle(GetAllLotsQuery())

    repo.get_all.assert_called_once()
    assert len(result) == 2
    assert result[0]["lot_number"] == "LOT-001"
    assert result[1]["lot_number"] == "LOT-002"


def test_get_all_lots_empty():
    repo = MagicMock()
    repo.get_all.return_value = []
    handler = GetAllLotsQueryHandler(repo)

    result = handler.handle(GetAllLotsQuery())
    assert result == []


# ---------------------------------------------------------------------------
# GetLotsByProductQueryHandler
# ---------------------------------------------------------------------------


def test_get_lots_by_product():
    lot1 = _make_lot(id=1, lot_number="LOT-001")
    lot2 = _make_lot(id=2, lot_number="LOT-002")
    repo = MagicMock()
    repo.filter_by.return_value = [lot1, lot2]
    handler = GetLotsByProductQueryHandler(repo)

    result = handler.handle(GetLotsByProductQuery(product_id=5))

    repo.filter_by.assert_called_once_with(product_id=5)
    assert len(result) == 2
    assert result[0]["lot_number"] == "LOT-001"


def test_get_lots_by_product_empty():
    repo = MagicMock()
    repo.filter_by.return_value = []
    handler = GetLotsByProductQueryHandler(repo)

    result = handler.handle(GetLotsByProductQuery(product_id=99))
    assert result == []


# ---------------------------------------------------------------------------
# GetExpiringLotsQueryHandler
# ---------------------------------------------------------------------------


def test_get_expiring_lots():
    expiry = date.today() + timedelta(days=10)
    lot = _make_lot(expiration_date=expiry, current_quantity=5)
    repo = MagicMock()
    repo.filter_by_spec.return_value = [lot]
    handler = GetExpiringLotsQueryHandler(repo)

    result = handler.handle(GetExpiringLotsQuery(days=30))

    repo.filter_by_spec.assert_called_once()
    assert len(result) == 1


def test_get_expiring_lots_empty():
    repo = MagicMock()
    repo.filter_by_spec.return_value = []
    handler = GetExpiringLotsQueryHandler(repo)

    result = handler.handle(GetExpiringLotsQuery(days=30))
    assert result == []


# ---------------------------------------------------------------------------
# GetLotByIdQueryHandler
# ---------------------------------------------------------------------------


def test_get_lot_by_id():
    lot = _make_lot()
    repo = MagicMock()
    repo.get_by_id.return_value = lot
    handler = GetLotByIdQueryHandler(repo)

    result = handler.handle(GetLotByIdQuery(id=1))

    repo.get_by_id.assert_called_once_with(1)
    assert result["id"] == 1


def test_get_lot_by_id_not_found_raises():
    repo = MagicMock()
    repo.get_by_id.return_value = None
    handler = GetLotByIdQueryHandler(repo)

    with pytest.raises(NotFoundError):
        handler.handle(GetLotByIdQuery(id=99))
