from sqlalchemy.orm import Session
from wireup import injectable

from src.catalog.product.domain.entities import Category, Product
from src.catalog.product.infra.mappers import CategoryMapper, ProductMapper
from src.catalog.product.infra.models import CategoryModel, ProductModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import BaseRepository


@injectable(lifetime="scoped")
class CategoryRepositoryImpl(BaseRepository[Category]):
    """Implementation of the CategoryRepository interface using SQLAlchemy
    This class provides methods to interact with the category data in the database
    through SQLAlchemy ORM.
    """

    __model__ = CategoryModel


@injectable(lifetime="scoped", as_type=Repository[Category])
def create_category_repository(
    session: Session, mapper: CategoryMapper
) -> Repository[Category]:
    """Factory function for creating CategoryRepository with generic type binding.

    Args:
        session: Scoped database session
        mapper: CategoryMapper instance

    Returns:
        Repository[Category]: Category repository implementation
    """
    return CategoryRepositoryImpl(session, mapper)


@injectable(lifetime="scoped")
class ProductRepositoryImpl(BaseRepository[Product]):
    """Implementation of the ProductRepository interface using SQLAlchemy

    This class provides methods to interact with the product data in the database
    through SQLAlchemy ORM.
    """

    __model__ = ProductModel


@injectable(lifetime="scoped", as_type=Repository[Product])
def create_product_repository(
    session: Session, mapper: ProductMapper
) -> Repository[Product]:
    """Factory function for creating ProductRepository with generic type binding.

    Args:
        session: Scoped database session
        mapper: ProductMapper instance

    Returns:
        Repository[Product]: Product repository implementation
    """
    return ProductRepositoryImpl(session, mapper)
