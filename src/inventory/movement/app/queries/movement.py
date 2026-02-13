from dataclasses import dataclass

from wireup import injectable

from src.inventory.movement.domain.entities import Movement
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetAllMovementsQuery(Query):
    """Query para obtener todos los movimientos con filtros opcionales"""

    product_id: int | None = None
    type: str | None = None
    from_date: str | None = None
    to_date: str | None = None
    limit: int | None = None
    offset: int | None = None


@injectable(lifetime="scoped")
class GetAllMovementsQueryHandler(QueryHandler[GetAllMovementsQuery, list[dict]]):
    def __init__(self, repo: Repository[Movement]):
        self.repo = repo

    def _handle(self, query: GetAllMovementsQuery) -> list[dict]:
        filters = {}
        if query.product_id is not None:
            filters["product_id"] = query.product_id
        if query.type is not None:
            filters["type"] = query.type
        # TODO: Implementar filtros por from_date y to_date cuando sea necesario

        movements = self.repo.filter_by(
            limit=query.limit, offset=query.offset, **filters
        )
        return [movement.dict() for movement in movements]


@dataclass
class GetMovementByIdQuery(Query):
    """Query para obtener un movimiento por su ID"""

    id: int = 0


@injectable(lifetime="scoped")
class GetMovementByIdQueryHandler(QueryHandler[GetMovementByIdQuery, dict | None]):
    def __init__(self, repo: Repository[Movement]):
        self.repo = repo

    def _handle(self, query: GetMovementByIdQuery) -> dict | None:
        movement = self.repo.get_by_id(query.id)
        if movement is None:
            return None
        return movement.dict()
