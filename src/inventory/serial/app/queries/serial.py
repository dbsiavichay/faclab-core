from dataclasses import dataclass

from wireup import injectable

from src.inventory.serial.domain.entities import SerialNumber
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class GetSerialsByProductQuery(Query):
    product_id: int = 0
    status: str | None = None


@dataclass
class GetSerialByNumberQuery(Query):
    serial_number: str = ""


@dataclass
class GetSerialByIdQuery(Query):
    id: int = 0


@injectable(lifetime="scoped")
class GetSerialsByProductQueryHandler(
    QueryHandler[GetSerialsByProductQuery, list[dict]]
):
    def __init__(self, repo: Repository[SerialNumber]):
        self.repo = repo

    def _handle(self, query: GetSerialsByProductQuery) -> list[dict]:
        if query.status is not None:
            serials = self.repo.filter_by(
                product_id=query.product_id, status=query.status
            )
        else:
            serials = self.repo.filter_by(product_id=query.product_id)
        return [s.dict() for s in serials]


@injectable(lifetime="scoped")
class GetSerialByNumberQueryHandler(QueryHandler[GetSerialByNumberQuery, dict]):
    def __init__(self, repo: Repository[SerialNumber]):
        self.repo = repo

    def _handle(self, query: GetSerialByNumberQuery) -> dict:
        serial = self.repo.first(serial_number=query.serial_number)
        if serial is None:
            raise NotFoundError(f"Serial number '{query.serial_number}' not found")
        return serial.dict()


@injectable(lifetime="scoped")
class GetSerialByIdQueryHandler(QueryHandler[GetSerialByIdQuery, dict]):
    def __init__(self, repo: Repository[SerialNumber]):
        self.repo = repo

    def _handle(self, query: GetSerialByIdQuery) -> dict:
        serial = self.repo.get_by_id(query.id)
        if serial is None:
            raise NotFoundError(f"Serial number with id {query.id} not found")
        return serial.dict()
