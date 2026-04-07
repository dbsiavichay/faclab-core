from dataclasses import dataclass

from wireup import injectable

from src.pos.cash.app.repositories import CashMovementRepository
from src.shared.app.queries import Query, QueryHandler


@dataclass
class GetCashMovementsQuery(Query):
    shift_id: int
    limit: int = 100
    offset: int = 0


@injectable(lifetime="scoped")
class GetCashMovementsQueryHandler(QueryHandler[GetCashMovementsQuery, dict]):
    def __init__(self, repo: CashMovementRepository):
        self.repo = repo

    def _handle(self, query: GetCashMovementsQuery) -> dict:
        return self.repo.paginate(
            limit=query.limit,
            offset=query.offset,
            shift_id=query.shift_id,
        )
