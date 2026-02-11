from dataclasses import dataclass
from typing import List, Optional

from src.catalog.product.domain.entities import Product
from src.catalog.product.domain.specifications import ProductByName, ProductInCategory
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetAllProductsQuery(Query):
    category_id: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class GetAllProductsQueryHandler(QueryHandler[GetAllProductsQuery, List[dict]]):
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def handle(self, query: GetAllProductsQuery) -> List[dict]:
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


class GetProductByIdQueryHandler(QueryHandler[GetProductByIdQuery, Optional[dict]]):
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def handle(self, query: GetProductByIdQuery) -> Optional[dict]:
        product = self.repo.get_by_id(query.product_id)
        return product.dict() if product else None


@dataclass
class SearchProductsQuery(Query):
    search_term: str
    limit: Optional[int] = 20


class SearchProductsQueryHandler(QueryHandler[SearchProductsQuery, List[dict]]):
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def handle(self, query: SearchProductsQuery) -> List[dict]:
        spec = ProductByName(query.search_term)
        products = self.repo.filter_by_spec(spec, limit=query.limit)
        return [p.dict() for p in products]
