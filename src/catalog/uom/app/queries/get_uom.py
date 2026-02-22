from dataclasses import dataclass

from wireup import injectable

from src.catalog.uom.domain.entities import UnitOfMeasure
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class GetAllUnitsOfMeasureQuery(Query):
    is_active: bool | None = None
    limit: int | None = None
    offset: int | None = None


@injectable(lifetime="scoped")
class GetAllUnitsOfMeasureQueryHandler(
    QueryHandler[GetAllUnitsOfMeasureQuery, list[dict]]
):
    def __init__(self, repo: Repository[UnitOfMeasure]):
        self.repo = repo

    def _handle(self, query: GetAllUnitsOfMeasureQuery) -> list[dict]:
        if query.is_active is not None:
            uoms = self.repo.filter_by(
                is_active=query.is_active,
                limit=query.limit,
                offset=query.offset,
            )
        else:
            uoms = self.repo.filter_by(limit=query.limit, offset=query.offset)
        return [u.dict() for u in uoms]


@dataclass
class GetUnitOfMeasureByIdQuery(Query):
    uom_id: int


@injectable(lifetime="scoped")
class GetUnitOfMeasureByIdQueryHandler(QueryHandler[GetUnitOfMeasureByIdQuery, dict]):
    def __init__(self, repo: Repository[UnitOfMeasure]):
        self.repo = repo

    def _handle(self, query: GetUnitOfMeasureByIdQuery) -> dict:
        uom = self.repo.get_by_id(query.uom_id)
        if uom is None:
            raise NotFoundError(f"Unit of measure with id {query.uom_id} not found")
        return uom.dict()
