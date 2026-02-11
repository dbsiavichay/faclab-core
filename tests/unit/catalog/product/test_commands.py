"""Unit tests for catalog product command handlers."""
import pytest
from unittest.mock import Mock

from src.catalog.product.app.commands import (
    CreateProductCommand,
    CreateProductCommandHandler,
    UpdateProductCommand,
    UpdateProductCommandHandler,
    DeleteProductCommand,
    DeleteProductCommandHandler,
    CreateCategoryCommand,
    CreateCategoryCommandHandler,
    UpdateCategoryCommand,
    UpdateCategoryCommandHandler,
    DeleteCategoryCommand,
    DeleteCategoryCommandHandler,
)
from src.catalog.product.domain.entities import Product, Category
from src.catalog.product.domain.events import (
    ProductCreated,
    ProductUpdated,
    ProductDeleted,
    CategoryCreated,
    CategoryUpdated,
    CategoryDeleted,
)
from src.shared.infra.events.event_bus import EventBus


@pytest.fixture(autouse=True)
def clear_event_bus():
    """Clear EventBus before each test."""
    EventBus.clear()
    yield
    EventBus.clear()


# Product Command Tests
def test_create_product_command_handler():
    """Test CreateProductCommandHandler creates a product and publishes event."""
    mock_repo = Mock()
    created_product = Product(id=1, sku="TEST-001", name="Test Product", category_id=1)
    mock_repo.create.return_value = created_product

    handler = CreateProductCommandHandler(mock_repo)
    command = CreateProductCommand(
        sku="TEST-001", name="Test Product", category_id=1
    )

    result = handler.handle(command)

    assert result["id"] == 1
    assert result["sku"] == "TEST-001"
    assert result["name"] == "Test Product"
    mock_repo.create.assert_called_once()


def test_create_product_publishes_event():
    """Test that CreateProductCommandHandler publishes ProductCreated event."""
    mock_repo = Mock()
    created_product = Product(id=1, sku="TEST-001", name="Test Product")
    mock_repo.create.return_value = created_product

    published_events = []

    def capture_event(event):
        published_events.append(event)

    EventBus.subscribe(ProductCreated, capture_event)

    handler = CreateProductCommandHandler(mock_repo)
    command = CreateProductCommand(sku="TEST-001", name="Test Product")
    handler.handle(command)

    assert len(published_events) == 1
    assert isinstance(published_events[0], ProductCreated)
    assert published_events[0].product_id == 1
    assert published_events[0].sku == "TEST-001"


def test_update_product_command_handler():
    """Test UpdateProductCommandHandler updates a product and publishes event."""
    mock_repo = Mock()
    existing_product = Product(id=1, sku="OLD-001", name="Old Name")
    updated_product = Product(id=1, sku="NEW-001", name="New Name")
    mock_repo.get_by_id.return_value = existing_product
    mock_repo.update.return_value = updated_product

    handler = UpdateProductCommandHandler(mock_repo)
    command = UpdateProductCommand(
        product_id=1, sku="NEW-001", name="New Name"
    )

    result = handler.handle(command)

    assert result["id"] == 1
    assert result["sku"] == "NEW-001"
    assert result["name"] == "New Name"
    mock_repo.update.assert_called_once()


def test_delete_product_command_handler():
    """Test DeleteProductCommandHandler deletes a product and publishes event."""
    mock_repo = Mock()

    handler = DeleteProductCommandHandler(mock_repo)
    command = DeleteProductCommand(product_id=1)

    result = handler.handle(command)

    assert result is None
    mock_repo.delete.assert_called_once_with(1)


# Category Command Tests
def test_create_category_command_handler():
    """Test CreateCategoryCommandHandler creates a category and publishes event."""
    mock_repo = Mock()
    created_category = Category(id=1, name="Electronics", description="Electronic items")
    mock_repo.create.return_value = created_category

    handler = CreateCategoryCommandHandler(mock_repo)
    command = CreateCategoryCommand(name="Electronics", description="Electronic items")

    result = handler.handle(command)

    assert result["id"] == 1
    assert result["name"] == "Electronics"
    assert result["description"] == "Electronic items"
    mock_repo.create.assert_called_once()


def test_create_category_publishes_event():
    """Test that CreateCategoryCommandHandler publishes CategoryCreated event."""
    mock_repo = Mock()
    created_category = Category(id=1, name="Electronics", description="Electronic items")
    mock_repo.create.return_value = created_category

    published_events = []

    def capture_event(event):
        published_events.append(event)

    EventBus.subscribe(CategoryCreated, capture_event)

    handler = CreateCategoryCommandHandler(mock_repo)
    command = CreateCategoryCommand(name="Electronics")
    handler.handle(command)

    assert len(published_events) == 1
    assert isinstance(published_events[0], CategoryCreated)
    assert published_events[0].category_id == 1
    assert published_events[0].name == "Electronics"


def test_update_category_command_handler():
    """Test UpdateCategoryCommandHandler updates a category and publishes event."""
    mock_repo = Mock()
    existing_category = Category(id=1, name="Old Name", description="Old desc")
    updated_category = Category(id=1, name="New Name", description="New desc")
    mock_repo.get_by_id.return_value = existing_category
    mock_repo.update.return_value = updated_category

    handler = UpdateCategoryCommandHandler(mock_repo)
    command = UpdateCategoryCommand(
        category_id=1, name="New Name", description="New desc"
    )

    result = handler.handle(command)

    assert result["id"] == 1
    assert result["name"] == "New Name"
    assert result["description"] == "New desc"
    mock_repo.update.assert_called_once()


def test_delete_category_command_handler():
    """Test DeleteCategoryCommandHandler deletes a category and publishes event."""
    mock_repo = Mock()

    handler = DeleteCategoryCommandHandler(mock_repo)
    command = DeleteCategoryCommand(category_id=1)

    result = handler.handle(command)

    assert result is None
    mock_repo.delete.assert_called_once_with(1)
