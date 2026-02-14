from sqlalchemy.orm import Session
from wireup import injectable

from src.catalog.product.domain.entities import Category, Product
from src.catalog.product.infra.mappers import CategoryMapper, ProductMapper
from src.catalog.product.infra.models import CategoryModel, ProductModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=Repository[Category])
class CategoryRepository(SqlAlchemyRepository[Category]):
    __model__ = CategoryModel

    def __init__(self, session: Session, mapper: CategoryMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=Repository[Product])
class ProductRepository(SqlAlchemyRepository[Product]):
    __model__ = ProductModel

    def __init__(self, session: Session, mapper: ProductMapper):
        super().__init__(session, mapper)
