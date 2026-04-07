from src.catalog.product.domain.entities import Category, Product
from src.shared.app.repositories import Repository


class CategoryRepository(Repository[Category]):
    pass


class ProductRepository(Repository[Product]):
    pass
