"""Unit tests for Movement query handlers"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from src.inventory.movement.app.queries import (
    GetAllMovementsQuery,
    GetAllMovementsQueryHandler,
    GetMovementByIdQuery,
    GetMovementByIdQueryHandler,
)
from src.inventory.movement.domain.constants import MovementType
from src.inventory.movement.domain.entities import Movement


@pytest.fixture
def mock_movement_repo():
    """Mock repository for Movement"""
    repo = Mock()
    return repo


def test_get_all_movements_query_handler(mock_movement_repo):
    """Test getting all movements"""
    # Arrange
    movements = [
        Movement(
            id=1,
            product_id=1,
            quantity=10,
            type=MovementType.IN,
            reason="Purchase",
        ),
        Movement(
            id=2,
            product_id=2,
            quantity=-5,
            type=MovementType.OUT,
            reason="Sale",
        ),
    ]
    mock_movement_repo.filter_by.return_value = movements

    query = GetAllMovementsQuery()
    handler = GetAllMovementsQueryHandler(mock_movement_repo)

    # Act
    result = handler.handle(query)

    # Assert
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 2
    mock_movement_repo.filter_by.assert_called_once_with(limit=None, offset=None)


def test_get_all_movements_with_product_filter(mock_movement_repo):
    """Test getting movements filtered by product_id"""
    # Arrange
    movements = [
        Movement(
            id=1,
            product_id=1,
            quantity=10,
            type=MovementType.IN,
        ),
    ]
    mock_movement_repo.filter_by.return_value = movements

    query = GetAllMovementsQuery(product_id=1)
    handler = GetAllMovementsQueryHandler(mock_movement_repo)

    # Act
    result = handler.handle(query)

    # Assert
    assert len(result) == 1
    assert result[0]["product_id"] == 1
    mock_movement_repo.filter_by.assert_called_once_with(
        limit=None, offset=None, product_id=1
    )


def test_get_all_movements_with_type_filter(mock_movement_repo):
    """Test getting movements filtered by type"""
    # Arrange
    movements = [
        Movement(
            id=1,
            product_id=1,
            quantity=10,
            type=MovementType.IN,
        ),
    ]
    mock_movement_repo.filter_by.return_value = movements

    query = GetAllMovementsQuery(type=MovementType.IN.value)
    handler = GetAllMovementsQueryHandler(mock_movement_repo)

    # Act
    result = handler.handle(query)

    # Assert
    assert len(result) == 1
    assert result[0]["type"] == MovementType.IN
    mock_movement_repo.filter_by.assert_called_once_with(
        limit=None, offset=None, type=MovementType.IN.value
    )


def test_get_all_movements_with_multiple_filters(mock_movement_repo):
    """Test getting movements with multiple filters"""
    # Arrange
    movements = [
        Movement(
            id=1,
            product_id=1,
            quantity=10,
            type=MovementType.IN,
        ),
    ]
    mock_movement_repo.filter_by.return_value = movements

    query = GetAllMovementsQuery(product_id=1, type=MovementType.IN.value)
    handler = GetAllMovementsQueryHandler(mock_movement_repo)

    # Act
    result = handler.handle(query)

    # Assert
    assert len(result) == 1
    mock_movement_repo.filter_by.assert_called_once_with(
        limit=None, offset=None, product_id=1, type=MovementType.IN.value
    )


def test_get_all_movements_empty(mock_movement_repo):
    """Test getting all movements when none exist"""
    # Arrange
    mock_movement_repo.filter_by.return_value = []

    query = GetAllMovementsQuery()
    handler = GetAllMovementsQueryHandler(mock_movement_repo)

    # Act
    result = handler.handle(query)

    # Assert
    assert len(result) == 0
    mock_movement_repo.filter_by.assert_called_once_with(limit=None, offset=None)


def test_get_all_movements_with_pagination(mock_movement_repo):
    """Test getting movements with pagination"""
    # Arrange
    movements = [
        Movement(
            id=1,
            product_id=1,
            quantity=10,
            type=MovementType.IN,
        ),
        Movement(
            id=2,
            product_id=2,
            quantity=-5,
            type=MovementType.OUT,
        ),
    ]
    mock_movement_repo.filter_by.return_value = movements

    query = GetAllMovementsQuery(limit=10, offset=5)
    handler = GetAllMovementsQueryHandler(mock_movement_repo)

    # Act
    result = handler.handle(query)

    # Assert
    assert len(result) == 2
    mock_movement_repo.filter_by.assert_called_once_with(limit=10, offset=5)


def test_get_movement_by_id_handler(mock_movement_repo):
    """Test getting a movement by ID"""
    # Arrange
    movement = Movement(
        id=1,
        product_id=1,
        quantity=10,
        type=MovementType.IN,
        reason="Test",
        date=datetime.now(),
    )
    mock_movement_repo.get_by_id.return_value = movement

    query = GetMovementByIdQuery(id=1)
    handler = GetMovementByIdQueryHandler(mock_movement_repo)

    # Act
    result = handler.handle(query)

    # Assert
    assert result is not None
    assert result["id"] == 1
    assert result["product_id"] == 1
    assert result["quantity"] == 10
    mock_movement_repo.get_by_id.assert_called_once_with(1)


def test_get_movement_by_id_not_found_returns_none(mock_movement_repo):
    """Test getting non-existent movement returns None"""
    # Arrange
    mock_movement_repo.get_by_id.return_value = None

    query = GetMovementByIdQuery(id=999)
    handler = GetMovementByIdQueryHandler(mock_movement_repo)

    # Act
    result = handler.handle(query)

    # Assert
    assert result is None
    mock_movement_repo.get_by_id.assert_called_once_with(999)
