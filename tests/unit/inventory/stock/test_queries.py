"""Unit tests for Stock query handlers"""

from unittest.mock import Mock

import pytest

from src.inventory.stock.app.queries import (
    GetAllStocksQuery,
    GetAllStocksQueryHandler,
    GetStockByIdQuery,
    GetStockByIdQueryHandler,
    GetStockByProductQuery,
    GetStockByProductQueryHandler,
)
from src.inventory.stock.domain.entities import Stock
from src.shared.domain.exceptions import NotFoundError


@pytest.fixture
def mock_stock_repo():
    """Mock repository for Stock"""
    repo = Mock()
    return repo


def test_get_all_stocks_query_handler(mock_stock_repo):
    """Test getting all stocks"""
    # Arrange
    stocks = [
        Stock(id=1, product_id=1, quantity=100),
        Stock(id=2, product_id=2, quantity=50),
    ]
    mock_stock_repo.filter_by.return_value = stocks

    query = GetAllStocksQuery()
    handler = GetAllStocksQueryHandler(mock_stock_repo)

    # Act
    result = handler.handle(query)

    # Assert
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["quantity"] == 100
    assert result[1]["id"] == 2
    assert result[1]["quantity"] == 50
    mock_stock_repo.filter_by.assert_called_once_with(limit=None, offset=None)


def test_get_all_stocks_with_product_filter(mock_stock_repo):
    """Test getting stocks filtered by product_id"""
    # Arrange
    stocks = [
        Stock(id=1, product_id=1, quantity=100),
    ]
    mock_stock_repo.filter_by.return_value = stocks

    query = GetAllStocksQuery(product_id=1)
    handler = GetAllStocksQueryHandler(mock_stock_repo)

    # Act
    result = handler.handle(query)

    # Assert
    assert len(result) == 1
    assert result[0]["product_id"] == 1
    assert result[0]["quantity"] == 100
    mock_stock_repo.filter_by.assert_called_once_with(
        limit=None, offset=None, product_id=1
    )


def test_get_all_stocks_empty(mock_stock_repo):
    """Test getting all stocks when none exist"""
    # Arrange
    mock_stock_repo.filter_by.return_value = []

    query = GetAllStocksQuery()
    handler = GetAllStocksQueryHandler(mock_stock_repo)

    # Act
    result = handler.handle(query)

    # Assert
    assert len(result) == 0
    mock_stock_repo.filter_by.assert_called_once_with(limit=None, offset=None)


def test_get_all_stocks_with_pagination(mock_stock_repo):
    """Test getting stocks with pagination"""
    # Arrange
    stocks = [
        Stock(id=1, product_id=1, quantity=100),
        Stock(id=2, product_id=2, quantity=50),
    ]
    mock_stock_repo.filter_by.return_value = stocks

    query = GetAllStocksQuery(limit=10, offset=5)
    handler = GetAllStocksQueryHandler(mock_stock_repo)

    # Act
    result = handler.handle(query)

    # Assert
    assert len(result) == 2
    mock_stock_repo.filter_by.assert_called_once_with(limit=10, offset=5)


def test_get_stock_by_id_handler(mock_stock_repo):
    """Test getting a stock by ID"""
    # Arrange
    stock = Stock(id=1, product_id=1, quantity=100, location_id=5)
    mock_stock_repo.get_by_id.return_value = stock

    query = GetStockByIdQuery(id=1)
    handler = GetStockByIdQueryHandler(mock_stock_repo)

    # Act
    result = handler.handle(query)

    # Assert
    assert result is not None
    assert result["id"] == 1
    assert result["product_id"] == 1
    assert result["quantity"] == 100
    assert result["location_id"] == 5
    mock_stock_repo.get_by_id.assert_called_once_with(1)


def test_get_stock_by_id_not_found_raises(mock_stock_repo):
    """Test getting non-existent stock raises NotFoundError"""
    # Arrange
    mock_stock_repo.get_by_id.return_value = None

    query = GetStockByIdQuery(id=999)
    handler = GetStockByIdQueryHandler(mock_stock_repo)

    # Act / Assert
    with pytest.raises(NotFoundError):
        handler.handle(query)
    mock_stock_repo.get_by_id.assert_called_once_with(999)


def test_get_stock_by_product_handler(mock_stock_repo):
    """Test getting stock by product_id"""
    # Arrange
    stock = Stock(id=1, product_id=1, quantity=100)
    mock_stock_repo.first.return_value = stock

    query = GetStockByProductQuery(product_id=1)
    handler = GetStockByProductQueryHandler(mock_stock_repo)

    # Act
    result = handler.handle(query)

    # Assert
    assert result is not None
    assert result["product_id"] == 1
    assert result["quantity"] == 100
    mock_stock_repo.first.assert_called_once_with(product_id=1)


def test_get_stock_by_product_not_found_raises(mock_stock_repo):
    """Test getting stock for non-existent product raises NotFoundError"""
    # Arrange
    mock_stock_repo.first.return_value = None

    query = GetStockByProductQuery(product_id=999)
    handler = GetStockByProductQueryHandler(mock_stock_repo)

    # Act / Assert
    with pytest.raises(NotFoundError):
        handler.handle(query)
    mock_stock_repo.first.assert_called_once_with(product_id=999)
