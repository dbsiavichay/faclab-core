from src.catalog.product.infra.models import ProductModel
from src.shared.domain.specifications import Specification


class ProductInCategory(Specification):
    def __init__(self, category_id: int):
        self.category_id = category_id

    def is_satisfied_by(self, product) -> bool:
        return product.category_id == self.category_id

    def to_sql_criteria(self):
        return [ProductModel.category_id == self.category_id]


class ProductByName(Specification):
    def __init__(self, name_pattern: str):
        self.name_pattern = name_pattern

    def is_satisfied_by(self, product) -> bool:
        return self.name_pattern.lower() in product.name.lower()

    def to_sql_criteria(self):
        return [ProductModel.name.ilike(f"%{self.name_pattern}%")]


class ProductBySku(Specification):
    def __init__(self, sku: str):
        self.sku = sku

    def is_satisfied_by(self, product) -> bool:
        return product.sku == self.sku

    def to_sql_criteria(self):
        return [ProductModel.sku == self.sku]
