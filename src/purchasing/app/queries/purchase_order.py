from dataclasses import dataclass

from wireup import injectable

from src.purchasing.domain.entities import PurchaseOrder
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class GetAllPurchaseOrdersQuery(Query):
    status: str | None = None
    supplier_id: int | None = None


@injectable(lifetime="scoped")
class GetAllPurchaseOrdersQueryHandler(
    QueryHandler[GetAllPurchaseOrdersQuery, list[dict]]
):
    def __init__(self, repo: Repository[PurchaseOrder]):
        self.repo = repo

    def _handle(self, query: GetAllPurchaseOrdersQuery) -> list[dict]:
        filters = {}
        if query.status is not None:
            filters["status"] = query.status
        if query.supplier_id is not None:
            filters["supplier_id"] = query.supplier_id

        orders = self.repo.filter_by(**filters) if filters else self.repo.get_all()

        return [order.dict() for order in orders]


@dataclass
class GetPurchaseOrderByIdQuery(Query):
    id: int = 0


@injectable(lifetime="scoped")
class GetPurchaseOrderByIdQueryHandler(QueryHandler[GetPurchaseOrderByIdQuery, dict]):
    def __init__(self, repo: Repository[PurchaseOrder]):
        self.repo = repo

    def _handle(self, query: GetPurchaseOrderByIdQuery) -> dict:
        order = self.repo.get_by_id(query.id)
        if order is None:
            raise NotFoundError(f"Purchase order with id {query.id} not found")
        return order.dict()
