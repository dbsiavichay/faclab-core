from dataclasses import dataclass

from wireup import injectable

from src.inventory.serial.app.repositories import SerialNumberRepository
from src.shared.app.queries import Query, QueryHandler
from src.shared.domain.exceptions import NotFoundError


@dataclass
class GetSerialsQuery(Query):
    product_id: int | None = None
    status: str | None = None
    limit: int | None = None
    offset: int | None = None


@dataclass
class GetSerialByNumberQuery(Query):
    serial_number: str = ""


@dataclass
class GetSerialByIdQuery(Query):
    id: int = 0


@injectable(lifetime="scoped")
class GetSerialsQueryHandler(QueryHandler[GetSerialsQuery, dict]):
    def __init__(self, repo: SerialNumberRepository):
        self.repo = repo

    def _handle(self, query: GetSerialsQuery) -> dict:
        kwargs = {}
        if query.product_id is not None:
            kwargs["product_id"] = query.product_id
        if query.status is not None:
            kwargs["status"] = query.status
        return self.repo.paginate(limit=query.limit, offset=query.offset, **kwargs)


@injectable(lifetime="scoped")
class GetSerialByNumberQueryHandler(QueryHandler[GetSerialByNumberQuery, dict]):
    def __init__(self, repo: SerialNumberRepository):
        self.repo = repo

    def _handle(self, query: GetSerialByNumberQuery) -> dict:
        serial = self.repo.first(serial_number=query.serial_number)
        if serial is None:
            raise NotFoundError(f"Serial number '{query.serial_number}' not found")
        return serial.dict()


@injectable(lifetime="scoped")
class GetSerialByIdQueryHandler(QueryHandler[GetSerialByIdQuery, dict]):
    def __init__(self, repo: SerialNumberRepository):
        self.repo = repo

    def _handle(self, query: GetSerialByIdQuery) -> dict:
        serial = self.repo.get_by_id(query.id)
        if serial is None:
            raise NotFoundError(f"Serial number with id {query.id} not found")
        return serial.dict()
