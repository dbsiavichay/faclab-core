from dataclasses import dataclass

from wireup import injectable

from src.catalog.uom.app.repositories import UnitOfMeasureRepository
from src.shared.app.queries import Query, QueryHandler
from src.shared.domain.exceptions import NotFoundError


@dataclass
class GetAllUnitsOfMeasureQuery(Query):
    is_active: bool | None = None
    limit: int | None = None
    offset: int | None = None


@injectable(lifetime="scoped")
class GetAllUnitsOfMeasureQueryHandler(QueryHandler[GetAllUnitsOfMeasureQuery, dict]):
    def __init__(self, repo: UnitOfMeasureRepository):
        self.repo = repo

    def _handle(self, query: GetAllUnitsOfMeasureQuery) -> dict:
        filter_kwargs = {}
        if query.is_active is not None:
            filter_kwargs["is_active"] = query.is_active

        uoms = self.repo.filter_by(
            limit=query.limit, offset=query.offset, **filter_kwargs
        )
        total = self.repo.count_by(**filter_kwargs)
        return {
            "total": total,
            "limit": query.limit,
            "offset": query.offset,
            "items": [u.dict() for u in uoms],
        }


@dataclass
class GetUnitOfMeasureByIdQuery(Query):
    uom_id: int


@injectable(lifetime="scoped")
class GetUnitOfMeasureByIdQueryHandler(QueryHandler[GetUnitOfMeasureByIdQuery, dict]):
    def __init__(self, repo: UnitOfMeasureRepository):
        self.repo = repo

    def _handle(self, query: GetUnitOfMeasureByIdQuery) -> dict:
        uom = self.repo.get_by_id(query.uom_id)
        if uom is None:
            raise NotFoundError(f"Unit of measure with id {query.uom_id} not found")
        return uom.dict()
