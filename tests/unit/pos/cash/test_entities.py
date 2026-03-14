from decimal import Decimal

from src.pos.cash.domain.entities import CashMovement, CashMovementType


def test_cash_movement_created_with_defaults():
    movement = CashMovement(
        shift_id=1,
        type=CashMovementType.IN,
        amount=Decimal("100.00"),
    )
    assert movement.shift_id == 1
    assert movement.type == CashMovementType.IN
    assert movement.amount == Decimal("100.00")
    assert movement.created_at is not None
    assert movement.reason is None
    assert movement.performed_by is None
    assert movement.id is None


def test_cash_movement_type_enum():
    assert CashMovementType.IN == "IN"
    assert CashMovementType.OUT == "OUT"


def test_cash_movement_with_all_fields():
    movement = CashMovement(
        shift_id=1,
        type=CashMovementType.OUT,
        amount=Decimal("50.00"),
        reason="Pago proveedor",
        performed_by="Juan",
    )
    assert movement.type == CashMovementType.OUT
    assert movement.reason == "Pago proveedor"
    assert movement.performed_by == "Juan"


def test_cash_movement_dict():
    movement = CashMovement(
        shift_id=1,
        type=CashMovementType.IN,
        amount=Decimal("200.00"),
        id=5,
    )
    d = movement.dict()
    assert d["shift_id"] == 1
    assert d["type"] == CashMovementType.IN
    assert d["amount"] == Decimal("200.00")
    assert d["id"] == 5
