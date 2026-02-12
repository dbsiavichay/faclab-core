"""Unit tests for Stock event handlers"""

from unittest.mock import Mock, patch

import pytest

from src.inventory.movement.domain.constants import MovementType
from src.inventory.movement.domain.events import MovementCreated
from src.inventory.stock.domain.entities import Stock
from src.inventory.stock.domain.events import StockCreated, StockUpdated
from src.inventory.stock.domain.exceptions import InsufficientStockError
from src.inventory.stock.infra.event_handlers import handle_movement_created
from src.shared.infra.events.event_bus import EventBus


@pytest.fixture(autouse=True)
def clear_event_bus():
    """Clear event bus before each test"""
    EventBus.clear()
    yield
    EventBus.clear()


@patch("src.wireup_container")
def test_handle_movement_created_creates_new_stock(mock_container):
    """Test that MovementCreated event creates new stock when none exists"""
    # Arrange
    mock_repo = Mock()
    mock_repo.first.return_value = None  # No existing stock

    new_stock = Stock(id=1, product_id=10, quantity=5)
    mock_repo.create.return_value = new_stock

    mock_container.get.return_value = mock_repo

    events_received = []

    def event_listener(event):
        events_received.append(event)

    EventBus.subscribe(StockCreated, event_listener)

    event = MovementCreated(
        aggregate_id=1,
        product_id=10,
        quantity=5,
        type=MovementType.IN.value,
        reason="Initial stock",
    )

    # Act
    handle_movement_created(event)

    # Assert
    mock_repo.first.assert_called_once_with(product_id=10)
    mock_repo.create.assert_called_once()

    # Verify the created stock
    created_stock = mock_repo.create.call_args[0][0]
    assert created_stock.product_id == 10
    assert created_stock.quantity == 5

    # Verify StockCreated event was published
    assert len(events_received) == 1
    stock_event = events_received[0]
    assert isinstance(stock_event, StockCreated)
    assert stock_event.aggregate_id == 1
    assert stock_event.product_id == 10
    assert stock_event.quantity == 5


@patch("src.wireup_container")
def test_handle_movement_created_updates_existing_stock(mock_container):
    """Test that MovementCreated event updates existing stock"""
    # Arrange
    existing_stock = Stock(id=1, product_id=10, quantity=100)
    mock_repo = Mock()
    mock_repo.first.return_value = existing_stock

    updated_stock = Stock(id=1, product_id=10, quantity=105)
    mock_repo.update.return_value = updated_stock

    mock_container.get.return_value = mock_repo

    events_received = []

    def event_listener(event):
        events_received.append(event)

    EventBus.subscribe(StockUpdated, event_listener)

    event = MovementCreated(
        aggregate_id=2,
        product_id=10,
        quantity=5,  # Adding 5 units
        type=MovementType.IN.value,
    )

    # Act
    handle_movement_created(event)

    # Assert
    mock_repo.first.assert_called_once_with(product_id=10)
    mock_repo.update.assert_called_once()

    # Verify the stock was updated
    updated = mock_repo.update.call_args[0][0]
    assert updated.quantity == 105

    # Verify StockUpdated event was published
    assert len(events_received) == 1
    stock_event = events_received[0]
    assert isinstance(stock_event, StockUpdated)
    assert stock_event.aggregate_id == 1
    assert stock_event.product_id == 10
    assert stock_event.old_quantity == 100
    assert stock_event.new_quantity == 105


@patch("src.wireup_container")
def test_handle_movement_created_decreases_stock_on_out(mock_container):
    """Test that OUT movement decreases stock"""
    # Arrange
    existing_stock = Stock(id=1, product_id=10, quantity=100)
    mock_repo = Mock()
    mock_repo.first.return_value = existing_stock

    updated_stock = Stock(id=1, product_id=10, quantity=95)
    mock_repo.update.return_value = updated_stock

    mock_container.get.return_value = mock_repo

    event = MovementCreated(
        aggregate_id=3,
        product_id=10,
        quantity=-5,  # Removing 5 units
        type=MovementType.OUT.value,
    )

    # Act
    handle_movement_created(event)

    # Assert
    mock_repo.first.assert_called_once_with(product_id=10)
    mock_repo.update.assert_called_once()

    # Verify the stock was decreased
    updated = mock_repo.update.call_args[0][0]
    assert updated.quantity == 95


@patch("src.wireup_container")
def test_handle_movement_created_insufficient_stock_raises(mock_container):
    """Test that insufficient stock raises exception"""
    # Arrange
    existing_stock = Stock(id=1, product_id=10, quantity=3)
    mock_repo = Mock()
    mock_repo.first.return_value = existing_stock

    mock_container.get.return_value = mock_repo

    event = MovementCreated(
        aggregate_id=4,
        product_id=10,
        quantity=-5,  # Trying to remove 5 units but only 3 available
        type=MovementType.OUT.value,
    )

    # Act & Assert
    with pytest.raises(InsufficientStockError) as exc_info:
        handle_movement_created(event)

    # InsufficientStockError stores product_id in data dict
    assert exc_info.value.data["product_id"] == 10
    mock_repo.update.assert_not_called()


@patch("src.wireup_container")
def test_handle_movement_created_publishes_stock_created_event(mock_container):
    """Test that StockCreated event is published when creating new stock"""
    # Arrange
    mock_repo = Mock()
    mock_repo.first.return_value = None

    new_stock = Stock(id=1, product_id=10, quantity=5, location="A1")
    mock_repo.create.return_value = new_stock

    mock_container.get.return_value = mock_repo

    events_received = []

    def event_listener(event: StockCreated):
        events_received.append(event)

    EventBus.subscribe(StockCreated, event_listener)

    event = MovementCreated(
        aggregate_id=1,
        product_id=10,
        quantity=5,
        type=MovementType.IN.value,
    )

    # Act
    handle_movement_created(event)

    # Assert
    assert len(events_received) == 1
    stock_event = events_received[0]
    assert stock_event.aggregate_id == 1
    assert stock_event.product_id == 10
    assert stock_event.quantity == 5
    assert stock_event.location == "A1"


@patch("src.wireup_container")
def test_handle_movement_created_publishes_stock_updated_event(mock_container):
    """Test that StockUpdated event is published when updating stock"""
    # Arrange
    existing_stock = Stock(id=1, product_id=10, quantity=100)
    mock_repo = Mock()
    mock_repo.first.return_value = existing_stock

    updated_stock = Stock(id=1, product_id=10, quantity=105)
    mock_repo.update.return_value = updated_stock

    mock_container.get.return_value = mock_repo

    events_received = []

    def event_listener(event: StockUpdated):
        events_received.append(event)

    EventBus.subscribe(StockUpdated, event_listener)

    event = MovementCreated(
        aggregate_id=2,
        product_id=10,
        quantity=5,
        type=MovementType.IN.value,
    )

    # Act
    handle_movement_created(event)

    # Assert
    assert len(events_received) == 1
    stock_event = events_received[0]
    assert stock_event.aggregate_id == 1
    assert stock_event.product_id == 10
    assert stock_event.old_quantity == 100
    assert stock_event.new_quantity == 105


@patch("src.wireup_container")
def test_handle_movement_created_with_location(mock_container):
    """Test creating stock with location"""
    # Arrange
    mock_repo = Mock()
    mock_repo.first.return_value = None

    new_stock = Stock(id=1, product_id=10, quantity=5, location="Warehouse A")
    mock_repo.create.return_value = new_stock

    mock_container.get.return_value = mock_repo

    event = MovementCreated(
        aggregate_id=1,
        product_id=10,
        quantity=5,
        type=MovementType.IN.value,
    )

    # Act
    handle_movement_created(event)

    # Assert
    created_stock = mock_repo.create.call_args[0][0]
    assert created_stock.product_id == 10
    assert created_stock.quantity == 5
