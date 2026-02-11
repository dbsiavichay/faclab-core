"""Unit tests for Movement command handlers"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from src.inventory.movement.app.commands import (
    CreateMovementCommand,
    CreateMovementCommandHandler,
)
from src.inventory.movement.domain.constants import MovementType
from src.inventory.movement.domain.entities import Movement
from src.inventory.movement.domain.events import MovementCreated
from src.inventory.movement.domain.exceptions import InvalidMovementTypeException
from src.shared.infra.events.event_bus import EventBus


@pytest.fixture
def mock_movement_repo():
    """Mock repository for Movement"""
    repo = Mock()
    return repo


@pytest.fixture(autouse=True)
def clear_event_bus():
    """Clear event bus before each test"""
    EventBus.clear()
    yield
    EventBus.clear()


def test_create_movement_in_command_handler_success(mock_movement_repo):
    """Test creating an IN movement successfully"""
    # Arrange
    command = CreateMovementCommand(
        product_id=1,
        quantity=10,
        type=MovementType.IN.value,
        reason="Purchase order #123",
    )

    mock_movement_repo.create.return_value = Movement(
        id=1,
        product_id=1,
        quantity=10,
        type=MovementType.IN,
        reason="Purchase order #123",
    )

    handler = CreateMovementCommandHandler(mock_movement_repo)

    # Act
    result = handler.handle(command)

    # Assert
    assert result["id"] == 1
    assert result["product_id"] == 1
    assert result["quantity"] == 10
    assert result["type"] == MovementType.IN
    mock_movement_repo.create.assert_called_once()


def test_create_movement_out_command_handler_success(mock_movement_repo):
    """Test creating an OUT movement successfully"""
    # Arrange
    command = CreateMovementCommand(
        product_id=1,
        quantity=-5,
        type=MovementType.OUT.value,
        reason="Sale #456",
    )

    mock_movement_repo.create.return_value = Movement(
        id=2,
        product_id=1,
        quantity=-5,
        type=MovementType.OUT,
        reason="Sale #456",
    )

    handler = CreateMovementCommandHandler(mock_movement_repo)

    # Act
    result = handler.handle(command)

    # Assert
    assert result["id"] == 2
    assert result["quantity"] == -5
    assert result["type"] == MovementType.OUT
    mock_movement_repo.create.assert_called_once()


def test_create_movement_publishes_movement_created_event(mock_movement_repo):
    """Test that creating a movement publishes MovementCreated event"""
    # Arrange
    events_received = []

    def event_listener(event: MovementCreated):
        events_received.append(event)

    EventBus.subscribe(MovementCreated, event_listener)

    command = CreateMovementCommand(
        product_id=1,
        quantity=10,
        type=MovementType.IN.value,
        reason="Test",
    )

    mock_movement_repo.create.return_value = Movement(
        id=1,
        product_id=1,
        quantity=10,
        type=MovementType.IN,
        reason="Test",
        date=datetime.now(),
    )

    handler = CreateMovementCommandHandler(mock_movement_repo)

    # Act
    handler.handle(command)

    # Assert
    assert len(events_received) == 1
    event = events_received[0]
    assert isinstance(event, MovementCreated)
    assert event.aggregate_id == 1
    assert event.product_id == 1
    assert event.quantity == 10
    assert event.type == MovementType.IN.value


def test_create_movement_in_with_negative_quantity_raises(mock_movement_repo):
    """Test that IN movement with negative quantity raises exception"""
    # Arrange
    command = CreateMovementCommand(
        product_id=1,
        quantity=-10,  # Invalid: negative for IN
        type=MovementType.IN.value,
    )

    handler = CreateMovementCommandHandler(mock_movement_repo)

    # Act & Assert
    with pytest.raises(InvalidMovementTypeException) as exc_info:
        handler.handle(command)

    # Check the detail attribute for the specific message
    assert hasattr(exc_info.value, 'detail')
    assert "positiva" in exc_info.value.detail.lower()
    mock_movement_repo.create.assert_not_called()


def test_create_movement_out_with_positive_quantity_raises(mock_movement_repo):
    """Test that OUT movement with positive quantity raises exception"""
    # Arrange
    command = CreateMovementCommand(
        product_id=1,
        quantity=10,  # Invalid: positive for OUT
        type=MovementType.OUT.value,
    )

    handler = CreateMovementCommandHandler(mock_movement_repo)

    # Act & Assert
    with pytest.raises(InvalidMovementTypeException) as exc_info:
        handler.handle(command)

    # Check the detail attribute for the specific message
    assert hasattr(exc_info.value, 'detail')
    assert "negativa" in exc_info.value.detail.lower()
    mock_movement_repo.create.assert_not_called()


def test_create_movement_zero_quantity_raises(mock_movement_repo):
    """Test that zero quantity raises exception"""
    # Arrange
    command = CreateMovementCommand(
        product_id=1,
        quantity=0,  # Invalid: zero
        type=MovementType.IN.value,
    )

    handler = CreateMovementCommandHandler(mock_movement_repo)

    # Act & Assert
    with pytest.raises(InvalidMovementTypeException) as exc_info:
        handler.handle(command)

    # Check the detail attribute for the specific message
    assert hasattr(exc_info.value, 'detail')
    assert "cero" in exc_info.value.detail.lower()
    mock_movement_repo.create.assert_not_called()


def test_create_movement_with_date(mock_movement_repo):
    """Test creating movement with specific date"""
    # Arrange
    specific_date = datetime(2026, 1, 15, 10, 30)
    command = CreateMovementCommand(
        product_id=1,
        quantity=10,
        type=MovementType.IN.value,
        date=specific_date,
    )

    mock_movement_repo.create.return_value = Movement(
        id=1,
        product_id=1,
        quantity=10,
        type=MovementType.IN,
        date=specific_date,
    )

    handler = CreateMovementCommandHandler(mock_movement_repo)

    # Act
    result = handler.handle(command)

    # Assert
    assert result["date"] == specific_date
    mock_movement_repo.create.assert_called_once()
