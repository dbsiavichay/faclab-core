from dataclasses import dataclass

from wireup import injectable

from src.catalog.product.app.repositories import CategoryRepository
from src.shared.app.queries import Query, QueryHandler
from src.shared.domain.exceptions import NotFoundError


@dataclass
class GetAllCategoriesQuery(Query):
    limit: int | None = None
    offset: int | None = None


@injectable(lifetime="scoped")
class GetAllCategoriesQueryHandler(QueryHandler[GetAllCategoriesQuery, dict]):
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    def _handle(self, query: GetAllCategoriesQuery) -> dict:
        return self.repo.paginate(limit=query.limit, offset=query.offset)


@dataclass
class GetCategoryByIdQuery(Query):
    category_id: int


@injectable(lifetime="scoped")
class GetCategoryByIdQueryHandler(QueryHandler[GetCategoryByIdQuery, dict]):
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    def _handle(self, query: GetCategoryByIdQuery) -> dict:
        category = self.repo.get_by_id(query.category_id)
        if category is None:
            raise NotFoundError(f"Category with id {query.category_id} not found")
        return category.dict()
