from dataclasses import dataclass

from wireup import injectable

from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError
from src.suppliers.domain.entities import Supplier


@dataclass
class GetAllSuppliersQuery(Query):
    is_active: bool | None = None
    limit: int | None = None
    offset: int | None = None


@injectable(lifetime="scoped")
class GetAllSuppliersQueryHandler(QueryHandler[GetAllSuppliersQuery, dict]):
    def __init__(self, repo: Repository[Supplier]):
        self.repo = repo

    def _handle(self, query: GetAllSuppliersQuery) -> dict:
        filter_kwargs = {}
        if query.is_active is not None:
            filter_kwargs["is_active"] = query.is_active
        return self.repo.paginate(
            limit=query.limit, offset=query.offset, **filter_kwargs
        )


@dataclass
class GetSupplierByIdQuery(Query):
    id: int = 0


@injectable(lifetime="scoped")
class GetSupplierByIdQueryHandler(QueryHandler[GetSupplierByIdQuery, dict]):
    def __init__(self, repo: Repository[Supplier]):
        self.repo = repo

    def _handle(self, query: GetSupplierByIdQuery) -> dict:
        supplier = self.repo.get_by_id(query.id)
        if supplier is None:
            raise NotFoundError(f"Supplier with id {query.id} not found")
        return supplier.dict()
