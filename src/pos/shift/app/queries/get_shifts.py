from dataclasses import dataclass

from wireup import injectable

from src.pos.shift.domain.entities import Shift
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class GetActiveShiftQuery(Query):
    """Query para obtener el turno activo"""

    pass


@injectable(lifetime="scoped")
class GetActiveShiftQueryHandler(QueryHandler[GetActiveShiftQuery, dict | None]):
    """Handler para obtener el turno activo"""

    def __init__(self, repo: Repository[Shift]):
        self.repo = repo

    def _handle(self, query: GetActiveShiftQuery) -> dict | None:
        shift = self.repo.first(status="OPEN")
        if shift is None:
            return None
        return shift.dict()


@dataclass
class GetShiftByIdQuery(Query):
    """Query para obtener un turno por ID"""

    shift_id: int


@injectable(lifetime="scoped")
class GetShiftByIdQueryHandler(QueryHandler[GetShiftByIdQuery, dict]):
    """Handler para obtener un turno por ID"""

    def __init__(self, repo: Repository[Shift]):
        self.repo = repo

    def _handle(self, query: GetShiftByIdQuery) -> dict:
        shift = self.repo.get_by_id(query.shift_id)
        if shift is None:
            raise NotFoundError(f"Shift with id {query.shift_id} not found")
        return shift.dict()


@dataclass
class GetAllShiftsQuery(Query):
    """Query para obtener todos los turnos"""

    status: str | None = None
    limit: int | None = None
    offset: int | None = None


@injectable(lifetime="scoped")
class GetAllShiftsQueryHandler(QueryHandler[GetAllShiftsQuery, dict]):
    """Handler para obtener todos los turnos"""

    def __init__(self, repo: Repository[Shift]):
        self.repo = repo

    def _handle(self, query: GetAllShiftsQuery) -> dict:
        filters = {}
        if query.status is not None:
            filters["status"] = query.status
        return self.repo.paginate(limit=query.limit, offset=query.offset, **filters)
