from unittest.mock import MagicMock, Mock, patch

from src.inventory.lot.domain.entities import Lot, MovementLotItem
from src.purchasing.domain.events import PurchaseOrderReceived


def _make_event(**overrides) -> PurchaseOrderReceived:
    defaults = {
        "aggregate_id": 1,
        "purchase_order_id": 1,
        "order_number": "PO-2026-0001",
        "is_complete": True,
        "items": [],
    }
    defaults.update(overrides)
    return PurchaseOrderReceived(**defaults)


def _make_lot(**overrides) -> Lot:
    defaults = {
        "id": 1,
        "product_id": 5,
        "lot_number": "LOT-001",
        "initial_quantity": 100,
        "current_quantity": 100,
    }
    defaults.update(overrides)
    return Lot(**defaults)


def _make_scope(lot_repo, movement_lot_item_repo, movement_repo):
    from src.inventory.lot.domain.entities import Lot, MovementLotItem
    from src.inventory.movement.domain.entities import Movement
    from src.shared.app.repositories import Repository

    mock_scope = Mock()

    def _get(cls):
        if cls is Repository[Lot]:
            return lot_repo
        if cls is Repository[MovementLotItem]:
            return movement_lot_item_repo
        if cls is Repository[Movement]:
            return movement_repo
        return MagicMock()

    mock_scope.get.side_effect = _get
    return mock_scope


# ---------------------------------------------------------------------------
# handle_purchase_order_received_lots
# ---------------------------------------------------------------------------


@patch("src.wireup_container")
def test_skips_items_without_lot_number(mock_container):
    """Items without lot_number should not trigger lot creation."""
    from src.inventory.lot.infra import event_handlers  # noqa: F401

    event = _make_event(
        items=[
            {
                "product_id": 5,
                "quantity": 10,
                "location_id": None,
                "lot_number": None,
                "serial_numbers": [],
            }
        ]
    )

    from src.inventory.lot.infra.event_handlers import (
        handle_purchase_order_received_lots,
    )

    handle_purchase_order_received_lots(event)

    mock_container.enter_scope.assert_not_called()


@patch("src.wireup_container")
def test_creates_new_lot_when_not_exists(mock_container):
    """Creates a new lot when lot_number is provided and doesn't exist."""
    from src.inventory.lot.infra import event_handlers  # noqa: F401

    lot = _make_lot()
    event = _make_event(
        items=[
            {
                "product_id": 5,
                "quantity": 10,
                "location_id": None,
                "lot_number": "LOT-001",
                "serial_numbers": [],
            }
        ]
    )

    lot_repo = MagicMock()
    lot_repo.first.return_value = None
    lot_repo.create.return_value = lot

    movement_lot_item_repo = MagicMock()
    movement_repo = MagicMock()
    movement_repo.filter_by.return_value = []

    mock_scope = _make_scope(lot_repo, movement_lot_item_repo, movement_repo)
    mock_container.enter_scope.return_value.__enter__.return_value = mock_scope

    from src.inventory.lot.infra.event_handlers import (
        handle_purchase_order_received_lots,
    )

    handle_purchase_order_received_lots(event)

    lot_repo.first.assert_called_once_with(product_id=5, lot_number="LOT-001")
    lot_repo.create.assert_called_once()
    created = lot_repo.create.call_args[0][0]
    assert created.product_id == 5
    assert created.lot_number == "LOT-001"
    assert created.initial_quantity == 10
    assert created.current_quantity == 10


@patch("src.wireup_container")
def test_updates_existing_lot_quantity(mock_container):
    """Updates current_quantity when lot already exists."""
    from src.inventory.lot.infra import event_handlers  # noqa: F401

    existing_lot = _make_lot(current_quantity=50)
    updated_lot = _make_lot(current_quantity=60)
    event = _make_event(
        items=[
            {
                "product_id": 5,
                "quantity": 10,
                "location_id": None,
                "lot_number": "LOT-001",
                "serial_numbers": [],
            }
        ]
    )

    lot_repo = MagicMock()
    lot_repo.first.return_value = existing_lot
    lot_repo.update.return_value = updated_lot

    movement_lot_item_repo = MagicMock()
    movement_repo = MagicMock()
    movement_repo.filter_by.return_value = []

    mock_scope = _make_scope(lot_repo, movement_lot_item_repo, movement_repo)
    mock_container.enter_scope.return_value.__enter__.return_value = mock_scope

    from src.inventory.lot.infra.event_handlers import (
        handle_purchase_order_received_lots,
    )

    handle_purchase_order_received_lots(event)

    lot_repo.update.assert_called_once()
    updated = lot_repo.update.call_args[0][0]
    assert updated.current_quantity == 60  # 50 + 10


@patch("src.wireup_container")
def test_creates_movement_lot_item_when_movement_exists(mock_container):
    """Creates MovementLotItem linking movement to lot."""
    from src.inventory.lot.infra import event_handlers  # noqa: F401
    from src.inventory.movement.domain.constants import MovementType
    from src.inventory.movement.domain.entities import Movement

    lot = _make_lot()
    movement = Movement(
        id=10,
        product_id=5,
        quantity=10,
        type=MovementType.IN,
        reference_type="purchase_order",
        reference_id=1,
    )
    event = _make_event(
        items=[
            {
                "product_id": 5,
                "quantity": 10,
                "location_id": None,
                "lot_number": "LOT-001",
                "serial_numbers": [],
            }
        ]
    )

    lot_repo = MagicMock()
    lot_repo.first.return_value = None
    lot_repo.create.return_value = lot

    movement_lot_item_repo = MagicMock()
    movement_lot_item_repo.create.return_value = MovementLotItem(
        id=1, movement_id=10, lot_id=1, quantity=10
    )

    movement_repo = MagicMock()
    movement_repo.filter_by.return_value = [movement]

    mock_scope = _make_scope(lot_repo, movement_lot_item_repo, movement_repo)
    mock_container.enter_scope.return_value.__enter__.return_value = mock_scope

    from src.inventory.lot.infra.event_handlers import (
        handle_purchase_order_received_lots,
    )

    handle_purchase_order_received_lots(event)

    movement_lot_item_repo.create.assert_called_once()
    created = movement_lot_item_repo.create.call_args[0][0]
    assert created.movement_id == 10
    assert created.lot_id == 1
    assert created.quantity == 10
