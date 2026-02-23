from dataclasses import dataclass

from wireup import injectable

from src.inventory.lot.domain.entities import Lot
from src.inventory.lot.domain.specifications import ExpiringLots
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class GetLotsByProductQuery(Query):
    product_id: int = 0


@dataclass
class GetExpiringLotsQuery(Query):
    days: int = 30


@dataclass
class GetLotByIdQuery(Query):
    id: int = 0


@injectable(lifetime="scoped")
class GetLotsByProductQueryHandler(QueryHandler[GetLotsByProductQuery, list[dict]]):
    def __init__(self, repo: Repository[Lot]):
        self.repo = repo

    def _handle(self, query: GetLotsByProductQuery) -> list[dict]:
        lots = self.repo.filter_by(product_id=query.product_id)
        return [lot.dict() for lot in lots]


@injectable(lifetime="scoped")
class GetExpiringLotsQueryHandler(QueryHandler[GetExpiringLotsQuery, list[dict]]):
    def __init__(self, repo: Repository[Lot]):
        self.repo = repo

    def _handle(self, query: GetExpiringLotsQuery) -> list[dict]:
        spec = ExpiringLots(days=query.days)
        lots = self.repo.filter_by_spec(spec)
        return [lot.dict() for lot in lots]


@injectable(lifetime="scoped")
class GetLotByIdQueryHandler(QueryHandler[GetLotByIdQuery, dict]):
    def __init__(self, repo: Repository[Lot]):
        self.repo = repo

    def _handle(self, query: GetLotByIdQuery) -> dict:
        lot = self.repo.get_by_id(query.id)
        if lot is None:
            raise NotFoundError(f"Lot with id {query.id} not found")
        return lot.dict()
