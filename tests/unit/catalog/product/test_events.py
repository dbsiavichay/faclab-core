"""Unit tests for catalog product domain events."""

from src.catalog.product.domain.events import (
    CategoryCreated,
    CategoryDeleted,
    CategoryUpdated,
    ProductCreated,
    ProductDeleted,
    ProductUpdated,
)


def test_product_created_event_to_dict():
    """Test ProductCreated event serialization."""
    event = ProductCreated(
        aggregate_id=1,
        product_id=1,
        sku="SKU-001",
        name="Test Product",
        category_id=1,
    )

    result = event.to_dict()

    assert result["event_type"] == "ProductCreated"
    assert result["aggregate_id"] == 1
    assert result["payload"]["product_id"] == 1
    assert result["payload"]["sku"] == "SKU-001"
    assert result["payload"]["name"] == "Test Product"
    assert result["payload"]["category_id"] == 1


def test_product_updated_event_to_dict():
    """Test ProductUpdated event serialization."""
    changes = {"name": {"old": "Old Name", "new": "New Name"}}
    event = ProductUpdated(
        aggregate_id=1,
        product_id=1,
        changes=changes,
    )

    result = event.to_dict()

    assert result["event_type"] == "ProductUpdated"
    assert result["aggregate_id"] == 1
    assert result["payload"]["product_id"] == 1
    assert result["payload"]["changes"] == changes


def test_product_deleted_event_to_dict():
    """Test ProductDeleted event serialization."""
    event = ProductDeleted(aggregate_id=1, product_id=1)

    result = event.to_dict()

    assert result["event_type"] == "ProductDeleted"
    assert result["aggregate_id"] == 1
    assert result["payload"]["product_id"] == 1


def test_category_created_event_to_dict():
    """Test CategoryCreated event serialization."""
    event = CategoryCreated(
        aggregate_id=1,
        category_id=1,
        name="Electronics",
    )

    result = event.to_dict()

    assert result["event_type"] == "CategoryCreated"
    assert result["aggregate_id"] == 1
    assert result["payload"]["category_id"] == 1
    assert result["payload"]["name"] == "Electronics"


def test_category_updated_event_to_dict():
    """Test CategoryUpdated event serialization."""
    changes = {"description": {"old": "Old desc", "new": "New desc"}}
    event = CategoryUpdated(
        aggregate_id=1,
        category_id=1,
        changes=changes,
    )

    result = event.to_dict()

    assert result["event_type"] == "CategoryUpdated"
    assert result["aggregate_id"] == 1
    assert result["payload"]["category_id"] == 1
    assert result["payload"]["changes"] == changes


def test_category_deleted_event_to_dict():
    """Test CategoryDeleted event serialization."""
    event = CategoryDeleted(aggregate_id=1, category_id=1)

    result = event.to_dict()

    assert result["event_type"] == "CategoryDeleted"
    assert result["aggregate_id"] == 1
    assert result["payload"]["category_id"] == 1
