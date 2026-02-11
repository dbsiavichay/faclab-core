from dataclasses import dataclass
from typing import List, Optional

from src.inventory.movement.app.types import MovementOutput
from src.inventory.movement.domain.entities import Movement
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetAllMovementsQuery(Query):
    """Query para obtener todos los movimientos con filtros opcionales"""

    product_id: Optional[int] = None
    type: Optional[str] = None


class GetAllMovementsQueryHandler(
    QueryHandler[GetAllMovementsQuery, List[MovementOutput]]
):
    def __init__(self, repo: Repository[Movement]):
        self.repo = repo

    def handle(self, query: GetAllMovementsQuery) -> List[MovementOutput]:
        filters = {}
        if query.product_id is not None:
            filters["product_id"] = query.product_id
        if query.type is not None:
            filters["type"] = query.type

        movements = self.repo.filter_by(**filters) if filters else self.repo.get_all()
        return [movement.dict() for movement in movements]


@dataclass
class GetMovementByIdQuery(Query):
    """Query para obtener un movimiento por su ID"""

    id: int = 0


class GetMovementByIdQueryHandler(
    QueryHandler[GetMovementByIdQuery, Optional[MovementOutput]]
):
    def __init__(self, repo: Repository[Movement]):
        self.repo = repo

    def handle(self, query: GetMovementByIdQuery) -> Optional[MovementOutput]:
        movement = self.repo.get_by_id(query.id)
        if movement is None:
            return None
        return movement.dict()
