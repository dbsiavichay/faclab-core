from dataclasses import dataclass

from wireup import injectable

from src.catalog.product.domain.entities import Product
from src.catalog.product.domain.specifications import ProductByName, ProductInCategory
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetAllProductsQuery(Query):
    category_id: int | None = None
    limit: int | None = None
    offset: int | None = None


@injectable(lifetime="scoped")
class GetAllProductsQueryHandler(QueryHandler[GetAllProductsQuery, list[dict]]):
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def _handle(self, query: GetAllProductsQuery) -> list[dict]:
        if query.category_id is not None:
            spec = ProductInCategory(query.category_id)
            products = self.repo.filter_by_spec(
                spec, limit=query.limit, offset=query.offset
            )
        else:
            products = self.repo.filter_by(limit=query.limit, offset=query.offset)
        return [p.dict() for p in products]


@dataclass
class GetProductByIdQuery(Query):
    product_id: int


@injectable(lifetime="scoped")
class GetProductByIdQueryHandler(QueryHandler[GetProductByIdQuery, dict | None]):
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def _handle(self, query: GetProductByIdQuery) -> dict | None:
        product = self.repo.get_by_id(query.product_id)
        return product.dict() if product else None


@dataclass
class SearchProductsQuery(Query):
    search_term: str
    limit: int | None = 20


@injectable(lifetime="scoped")
class SearchProductsQueryHandler(QueryHandler[SearchProductsQuery, list[dict]]):
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def _handle(self, query: SearchProductsQuery) -> list[dict]:
        spec = ProductByName(query.search_term)
        products = self.repo.filter_by_spec(spec, limit=query.limit)
        return [p.dict() for p in products]
