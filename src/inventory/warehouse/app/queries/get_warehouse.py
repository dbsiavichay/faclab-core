from dataclasses import dataclass

from wireup import injectable

from src.inventory.warehouse.domain.entities import Warehouse
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class GetAllWarehousesQuery(Query):
    is_active: bool | None = None


@injectable(lifetime="scoped")
class GetAllWarehousesQueryHandler(QueryHandler[GetAllWarehousesQuery, list[dict]]):
    def __init__(self, repo: Repository[Warehouse]):
        self.repo = repo

    def _handle(self, query: GetAllWarehousesQuery) -> list[dict]:
        if query.is_active is not None:
            warehouses = self.repo.filter_by(is_active=query.is_active)
        else:
            warehouses = self.repo.get_all()
        return [w.dict() for w in warehouses]


@dataclass
class GetWarehouseByIdQuery(Query):
    warehouse_id: int


@injectable(lifetime="scoped")
class GetWarehouseByIdQueryHandler(QueryHandler[GetWarehouseByIdQuery, dict]):
    def __init__(self, repo: Repository[Warehouse]):
        self.repo = repo

    def _handle(self, query: GetWarehouseByIdQuery) -> dict:
        warehouse = self.repo.get_by_id(query.warehouse_id)
        if warehouse is None:
            raise NotFoundError(f"Warehouse {query.warehouse_id} not found")
        return warehouse.dict()
