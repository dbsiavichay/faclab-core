from dataclasses import dataclass

from wireup import injectable

from src.inventory.lot.domain.entities import Lot
from src.inventory.lot.domain.specifications import ExpiringLots
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
        if query.expiring_in_days is not None:
            spec = ExpiringLots(days=query.expiring_in_days)
            if query.product_id is not None:
                from src.inventory.lot.domain.specifications import LotsByProduct

                spec = spec & LotsByProduct(query.product_id)
            return self.repo.paginate_by_spec(
                spec, limit=query.limit, offset=query.offset
            )
        if query.product_id is not None:
            return self.repo.paginate(
                product_id=query.product_id,
                limit=query.limit,
                offset=query.offset,
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
