"""Integration tests for Movement-Stock event-driven flow"""

from unittest.mock import Mock, patch

import pytest

from src.inventory.movement.app.commands import (
    CreateMovementCommand,
    CreateMovementCommandHandler,
)
from src.inventory.movement.domain.constants import MovementType
from src.inventory.movement.domain.entities import Movement
from src.inventory.movement.domain.events import MovementCreated
from src.inventory.stock.domain.entities import Stock
from src.inventory.stock.domain.events import StockCreated, StockUpdated
from src.inventory.stock.infra.event_handlers import handle_movement_created
from src.sales.domain.events import SaleCancelled, SaleConfirmed
from src.shared.infra.events.event_bus import EventBus


@pytest.fixture(autouse=True)
def clear_event_bus():
    """Clear event bus before each test"""
    EventBus.clear()
    # Register the stock event handler
    EventBus.subscribe(MovementCreated, handle_movement_created)
    yield
    EventBus.clear()


@patch("src.container")
def test_create_movement_triggers_stock_update_via_event(mock_stock_container):
    """
    Integration test: Creating a movement publishes MovementCreated,
    which triggers handle_movement_created, which updates stock.
    """
    # Arrange
    mock_movement_repo = Mock()
    mock_stock_repo = Mock()

    # Setup: No existing stock
    mock_stock_repo.first.return_value = None

    new_stock = Stock(id=1, product_id=10, quantity=10)
    mock_stock_repo.create.return_value = new_stock

    mock_stock_container.resolve.return_value = mock_stock_repo

    # Movement to create
    created_movement = Movement(
        id=1,
        product_id=10,
        quantity=10,
        type=MovementType.IN,
        reason="Initial stock",
    )
    mock_movement_repo.create.return_value = created_movement

    # Track stock events
    stock_events = []

    def stock_listener(event):
        stock_events.append(event)

    EventBus.subscribe(StockCreated, stock_listener)

    # Create command handler
    handler = CreateMovementCommandHandler(mock_movement_repo)
    command = CreateMovementCommand(
        product_id=10,
        quantity=10,
        type=MovementType.IN.value,
        reason="Initial stock",
    )

    # Act
    result = handler.handle(command)

    # Assert
    # 1. Movement was created
    assert result["id"] == 1
    assert result["product_id"] == 10
    mock_movement_repo.create.assert_called_once()

    # 2. Stock was created via event handler
    mock_stock_repo.create.assert_called_once()
    created_stock = mock_stock_repo.create.call_args[0][0]
    assert created_stock.product_id == 10
    assert created_stock.quantity == 10

    # 3. StockCreated event was published
    assert len(stock_events) == 1
    assert stock_events[0].product_id == 10


@patch("src.container")
@patch("src.container")
def test_sale_confirmed_creates_movement_and_updates_stock(
    mock_inventory_container, mock_stock_container
):
    """
    Integration test: SaleConfirmed → CreateMovement → MovementCreated → Stock updated
    """
    # Arrange
    from src.inventory.infra.event_handlers import handle_sale_confirmed

    # Register the sale confirmed handler
    EventBus.subscribe(SaleConfirmed, handle_sale_confirmed)

    mock_movement_repo = Mock()
    mock_stock_repo = Mock()

    # Existing stock
    existing_stock = Stock(id=1, product_id=10, quantity=100)
    mock_stock_repo.first.return_value = existing_stock

    updated_stock = Stock(id=1, product_id=10, quantity=95)
    mock_stock_repo.update.return_value = updated_stock

    mock_stock_container.resolve.return_value = mock_stock_repo

    # Movement created by sale confirmation
    created_movement = Movement(
        id=1,
        product_id=10,
        quantity=-5,
        type=MovementType.OUT,
        reason="Sale #123 confirmed",
    )
    mock_movement_repo.create.return_value = created_movement

    # Mock command handler
    mock_command_handler = Mock()
    mock_command_handler.handle.return_value = created_movement.dict()
    mock_inventory_container.resolve.return_value = mock_command_handler

    # Track events
    stock_events = []

    def stock_listener(event):
        stock_events.append(event)

    EventBus.subscribe(StockUpdated, stock_listener)

    # Sale confirmed event
    sale_event = SaleConfirmed(
        aggregate_id=123,
        sale_id=123,
        customer_id=1,
        items=[{"product_id": 10, "quantity": 5, "unit_price": 10.0}],
        total=50.0,
    )

    # Act
    EventBus.publish(sale_event)

    # Assert
    # 1. Movement command handler was called
    mock_command_handler.handle.assert_called_once()
    call_args = mock_command_handler.handle.call_args[0][0]
    assert call_args.product_id == 10
    assert call_args.quantity == -5
    assert call_args.type == MovementType.OUT.value

    # 2. Stock was updated
    mock_stock_repo.update.assert_called_once()

    # 3. StockUpdated event was published
    assert len(stock_events) == 1
    assert stock_events[0].product_id == 10
    assert stock_events[0].old_quantity == 100
    assert stock_events[0].new_quantity == 95


@patch("src.container")
@patch("src.container")
def test_sale_cancelled_reverts_stock_via_event(
    mock_inventory_container, mock_stock_container
):
    """
    Integration test: SaleCancelled (was_confirmed=True) → CreateMovement IN → Stock restored
    """
    # Arrange
    from src.inventory.infra.event_handlers import handle_sale_cancelled

    EventBus.subscribe(SaleCancelled, handle_sale_cancelled)

    mock_movement_repo = Mock()
    mock_stock_repo = Mock()

    # Stock after sale was confirmed (reduced by 5)
    existing_stock = Stock(id=1, product_id=10, quantity=95)
    mock_stock_repo.first.return_value = existing_stock

    # Stock after reversal
    restored_stock = Stock(id=1, product_id=10, quantity=100)
    mock_stock_repo.update.return_value = restored_stock

    mock_stock_container.resolve.return_value = mock_stock_repo

    # Reversal movement
    reversal_movement = Movement(
        id=2,
        product_id=10,
        quantity=5,  # Positive for IN
        type=MovementType.IN,
        reason="Sale #123 cancelled - reversal",
    )
    mock_movement_repo.create.return_value = reversal_movement

    # Mock command handler
    mock_command_handler = Mock()
    mock_command_handler.handle.return_value = reversal_movement.dict()
    mock_inventory_container.resolve.return_value = mock_command_handler

    # Track events
    stock_events = []

    def stock_listener(event):
        stock_events.append(event)

    EventBus.subscribe(StockUpdated, stock_listener)

    # Sale cancelled event (was confirmed)
    cancel_event = SaleCancelled(
        aggregate_id=123,
        sale_id=123,
        customer_id=1,
        items=[{"product_id": 10, "quantity": 5}],
        reason="Customer request",
        was_confirmed=True,  # Stock needs to be restored
    )

    # Act
    EventBus.publish(cancel_event)

    # Assert
    # 1. Movement command handler was called
    mock_command_handler.handle.assert_called_once()
    call_args = mock_command_handler.handle.call_args[0][0]
    assert call_args.product_id == 10
    assert call_args.quantity == 5  # Positive for reversal
    assert call_args.type == MovementType.IN.value

    # 2. Stock was restored
    mock_stock_repo.update.assert_called_once()

    # 3. StockUpdated event was published
    assert len(stock_events) == 1
    assert stock_events[0].product_id == 10
    assert stock_events[0].old_quantity == 95
    assert stock_events[0].new_quantity == 100


@patch("src.container")
def test_sale_cancelled_draft_no_stock_change(mock_inventory_container):
    """
    Integration test: SaleCancelled (was_confirmed=False) → No movement created
    """
    # Arrange
    from src.inventory.infra.event_handlers import handle_sale_cancelled

    EventBus.subscribe(SaleCancelled, handle_sale_cancelled)

    mock_command_handler = Mock()
    mock_inventory_container.resolve.return_value = mock_command_handler

    # Sale cancelled event (was NOT confirmed)
    cancel_event = SaleCancelled(
        aggregate_id=123,
        sale_id=123,
        customer_id=1,
        items=[{"product_id": 10, "quantity": 5}],
        reason="Customer request",
        was_confirmed=False,  # No stock to restore
    )

    # Act
    EventBus.publish(cancel_event)

    # Assert
    # No movement should be created for draft sales
    mock_command_handler.handle.assert_not_called()


@patch("src.container")
def test_multiple_movements_accumulate_stock(mock_stock_container):
    """
    Integration test: Multiple movements update stock cumulatively
    """
    # Arrange
    mock_movement_repo = Mock()
    mock_stock_repo = Mock()

    # Start with no stock
    call_count = [0]

    def mock_first(product_id):
        call_count[0] += 1
        if call_count[0] == 1:
            return None  # First call: no stock
        elif call_count[0] == 2:
            return Stock(id=1, product_id=10, quantity=10)  # After first movement
        elif call_count[0] == 3:
            return Stock(id=1, product_id=10, quantity=20)  # After second movement

    mock_stock_repo.first.side_effect = mock_first
    mock_stock_repo.create.return_value = Stock(id=1, product_id=10, quantity=10)
    mock_stock_repo.update.side_effect = [
        Stock(id=1, product_id=10, quantity=20),
        Stock(id=1, product_id=10, quantity=15),
    ]

    mock_stock_container.resolve.return_value = mock_stock_repo

    handler = CreateMovementCommandHandler(mock_movement_repo)

    # Movement 1: +10
    mock_movement_repo.create.return_value = Movement(
        id=1, product_id=10, quantity=10, type=MovementType.IN
    )
    command1 = CreateMovementCommand(product_id=10, quantity=10, type=MovementType.IN.value)
    handler.handle(command1)

    # Movement 2: +10 (total 20)
    mock_movement_repo.create.return_value = Movement(
        id=2, product_id=10, quantity=10, type=MovementType.IN
    )
    command2 = CreateMovementCommand(product_id=10, quantity=10, type=MovementType.IN.value)
    handler.handle(command2)

    # Movement 3: -5 (total 15)
    mock_movement_repo.create.return_value = Movement(
        id=3, product_id=10, quantity=-5, type=MovementType.OUT
    )
    command3 = CreateMovementCommand(product_id=10, quantity=-5, type=MovementType.OUT.value)
    handler.handle(command3)

    # Assert
    # 1 create + 2 updates
    assert mock_stock_repo.create.call_count == 1
    assert mock_stock_repo.update.call_count == 2
