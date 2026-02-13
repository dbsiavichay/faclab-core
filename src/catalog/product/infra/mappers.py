from wireup import injectable

from src.catalog.product.domain.entities import Category, Product
from src.catalog.product.infra.models import CategoryModel, ProductModel
from src.shared.infra.mappers import Mapper


@injectable
class CategoryMapper(Mapper[Category, CategoryModel]):
    __entity__ = Category


@injectable
class ProductMapper(Mapper[Product, ProductModel]):
    __entity__ = Product
    __exclude_fields__ = frozenset({"created_at"})
