from src.catalog.product.domain.entities import Category, Product
from src.catalog.product.infra.models import CategoryModel, ProductModel
from src.shared.infra.repositories import BaseRepository


class CategoryRepositoryImpl(BaseRepository[Category]):
    """Implementation of the CategoryRepository interface using SQLAlchemy
    This class provides methods to interact with the category data in the database
    through SQLAlchemy ORM.
    """

    __model__ = CategoryModel


class ProductRepositoryImpl(BaseRepository[Product]):
    """Implementation of the ProductRepository interface using SQLAlchemy

    This class provides methods to interact with the product data in the database
    through SQLAlchemy ORM.
    """

    __model__ = ProductModel
