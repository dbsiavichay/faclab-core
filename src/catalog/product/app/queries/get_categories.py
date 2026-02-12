from dataclasses import dataclass

from wireup import injectable

from src.catalog.product.domain.entities import Category
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetAllCategoriesQuery(Query):
    limit: int | None = None
    offset: int | None = None


@injectable(lifetime="scoped")
class GetAllCategoriesQueryHandler(QueryHandler[GetAllCategoriesQuery, list[dict]]):
    def __init__(self, repo: Repository[Category]):
        self.repo = repo

    def _handle(self, query: GetAllCategoriesQuery) -> list[dict]:
        categories = self.repo.filter_by(limit=query.limit, offset=query.offset)
        return [c.dict() for c in categories]


@dataclass
class GetCategoryByIdQuery(Query):
    category_id: int


@injectable(lifetime="scoped")
class GetCategoryByIdQueryHandler(QueryHandler[GetCategoryByIdQuery, dict | None]):
    def __init__(self, repo: Repository[Category]):
        self.repo = repo

    def _handle(self, query: GetCategoryByIdQuery) -> dict | None:
        category = self.repo.get_by_id(query.category_id)
        return category.dict() if category else None
