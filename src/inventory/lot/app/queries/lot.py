from dataclasses import dataclass

from wireup import injectable

from src.inventory.lot.domain.entities import Lot
from src.inventory.lot.domain.specifications import ExpiringLots, LotsByProduct
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class GetAllLotsQuery(Query):
    product_id: int | None = None
    expiring_in_days: int | None = None
    limit: int | None = None
    offset: int | None = None


@dataclass
class GetLotByIdQuery(Query):
    id: int = 0


@injectable(lifetime="scoped")
class GetAllLotsQueryHandler(QueryHandler[GetAllLotsQuery, dict]):
    def __init__(self, repo: Repository[Lot]):
        self.repo = repo

    def _handle(self, query: GetAllLotsQuery) -> dict:
        spec = None
        if query.product_id is not None:
            spec = LotsByProduct(query.product_id)
        if query.expiring_in_days is not None:
            expiring_spec = ExpiringLots(days=query.expiring_in_days)
            spec = (spec & expiring_spec) if spec else expiring_spec

        if spec is not None:
            return self.repo.paginate_by_spec(
                spec, limit=query.limit, offset=query.offset
            )
        return self.repo.paginate(limit=query.limit, offset=query.offset)


@injectable(lifetime="scoped")
class GetLotByIdQueryHandler(QueryHandler[GetLotByIdQuery, dict]):
    def __init__(self, repo: Repository[Lot]):
        self.repo = repo

    def _handle(self, query: GetLotByIdQuery) -> dict:
        lot = self.repo.get_by_id(query.id)
        if lot is None:
            raise NotFoundError(f"Lot with id {query.id} not found")
        return lot.dict()
