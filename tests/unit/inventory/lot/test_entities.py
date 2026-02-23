from datetime import date, timedelta

from src.inventory.lot.domain.entities import Lot, MovementLotItem


def _make_lot(**overrides) -> Lot:
    defaults = {
        "id": 1,
        "product_id": 5,
        "lot_number": "LOT-2026-001",
        "initial_quantity": 100,
        "current_quantity": 80,
    }
    defaults.update(overrides)
    return Lot(**defaults)


# ---------------------------------------------------------------------------
# Lot.is_expired
# ---------------------------------------------------------------------------


def test_lot_is_expired_no_expiration_date():
    lot = _make_lot(expiration_date=None)
    assert lot.is_expired is False


def test_lot_is_expired_future_expiration():
    future_date = date.today() + timedelta(days=30)
    lot = _make_lot(expiration_date=future_date)
    assert lot.is_expired is False


def test_lot_is_expired_past_expiration():
    past_date = date.today() - timedelta(days=1)
    lot = _make_lot(expiration_date=past_date)
    assert lot.is_expired is True


def test_lot_is_expired_today_expiration():
    # today is NOT > today, so not expired
    lot = _make_lot(expiration_date=date.today())
    assert lot.is_expired is False


# ---------------------------------------------------------------------------
# Lot.days_to_expiry
# ---------------------------------------------------------------------------


def test_lot_days_to_expiry_no_expiration_date():
    lot = _make_lot(expiration_date=None)
    assert lot.days_to_expiry is None


def test_lot_days_to_expiry_future():
    future_date = date.today() + timedelta(days=15)
    lot = _make_lot(expiration_date=future_date)
    assert lot.days_to_expiry == 15


def test_lot_days_to_expiry_past():
    past_date = date.today() - timedelta(days=5)
    lot = _make_lot(expiration_date=past_date)
    assert lot.days_to_expiry == -5


def test_lot_days_to_expiry_today():
    lot = _make_lot(expiration_date=date.today())
    assert lot.days_to_expiry == 0


# ---------------------------------------------------------------------------
# MovementLotItem construction
# ---------------------------------------------------------------------------


def test_movement_lot_item_creation():
    item = MovementLotItem(id=1, movement_id=10, lot_id=3, quantity=50)
    assert item.movement_id == 10
    assert item.lot_id == 3
    assert item.quantity == 50
