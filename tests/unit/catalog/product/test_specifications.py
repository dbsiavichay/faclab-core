"""Unit tests for catalog product specifications."""

from src.catalog.product.domain.entities import Product
from src.catalog.product.domain.specifications import (
    ProductByName,
    ProductBySku,
    ProductInCategory,
)
from src.catalog.product.infra.models import ProductModel


def test_product_in_category_spec():
    """Test ProductInCategory specification with entity."""
    product_in_category = Product(id=1, sku="SKU-001", name="Product 1", category_id=1)
    product_not_in_category = Product(id=2, sku="SKU-002", name="Product 2", category_id=2)

    spec = ProductInCategory(category_id=1)

    assert spec.is_satisfied_by(product_in_category) is True
    assert spec.is_satisfied_by(product_not_in_category) is False


def test_product_in_category_sql_criteria():
    """Test ProductInCategory specification SQL criteria generation."""
    spec = ProductInCategory(category_id=1)

    criteria = spec.to_sql_criteria()

    assert len(criteria) == 1
    # Verify it's a SQLAlchemy comparison
    assert str(criteria[0].compile()) == str((ProductModel.category_id == 1).compile())


def test_product_by_name_spec():
    """Test ProductByName specification with entity."""
    product_match = Product(id=1, sku="SKU-001", name="Laptop Computer")
    product_no_match = Product(id=2, sku="SKU-002", name="Mouse")

    spec = ProductByName(name_pattern="Laptop")

    assert spec.is_satisfied_by(product_match) is True
    assert spec.is_satisfied_by(product_no_match) is False


def test_product_by_name_case_insensitive():
    """Test ProductByName specification is case-insensitive."""
    product = Product(id=1, sku="SKU-001", name="Laptop Computer")

    spec = ProductByName(name_pattern="laptop")

    assert spec.is_satisfied_by(product) is True


def test_product_by_name_sql_criteria():
    """Test ProductByName specification SQL criteria generation."""
    spec = ProductByName(name_pattern="Laptop")

    criteria = spec.to_sql_criteria()

    assert len(criteria) == 1


def test_product_by_sku_spec():
    """Test ProductBySku specification with entity."""
    product_match = Product(id=1, sku="SKU-001", name="Product 1")
    product_no_match = Product(id=2, sku="SKU-002", name="Product 2")

    spec = ProductBySku(sku="SKU-001")

    assert spec.is_satisfied_by(product_match) is True
    assert spec.is_satisfied_by(product_no_match) is False


def test_product_by_sku_sql_criteria():
    """Test ProductBySku specification SQL criteria generation."""
    spec = ProductBySku(sku="SKU-001")

    criteria = spec.to_sql_criteria()

    assert len(criteria) == 1
    assert str(criteria[0].compile()) == str((ProductModel.sku == "SKU-001").compile())


def test_combined_specifications():
    """Test combining specifications with AND operator."""
    product_match = Product(id=1, sku="SKU-001", name="Laptop Computer", category_id=1)
    product_no_match = Product(id=2, sku="SKU-002", name="Laptop Computer", category_id=2)

    spec = ProductInCategory(category_id=1) & ProductByName(name_pattern="Laptop")

    assert spec.is_satisfied_by(product_match) is True
    assert spec.is_satisfied_by(product_no_match) is False
