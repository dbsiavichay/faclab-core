from dataclasses import dataclass

from wireup import injectable

from src.inventory.location.domain.entities import Location
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class GetAllLocationsQuery(Query):
    warehouse_id: int | None = None
    is_active: bool | None = None


@injectable(lifetime="scoped")
class GetAllLocationsQueryHandler(QueryHandler[GetAllLocationsQuery, list[dict]]):
    def __init__(self, repo: Repository[Location]):
        self.repo = repo

    def _handle(self, query: GetAllLocationsQuery) -> list[dict]:
        filters = {}
        if query.warehouse_id is not None:
            filters["warehouse_id"] = query.warehouse_id
        if query.is_active is not None:
            filters["is_active"] = query.is_active

        locations = self.repo.filter_by(**filters) if filters else self.repo.get_all()
        return [loc.dict() for loc in locations]


@dataclass
class GetLocationByIdQuery(Query):
    location_id: int


@injectable(lifetime="scoped")
class GetLocationByIdQueryHandler(QueryHandler[GetLocationByIdQuery, dict]):
    def __init__(self, repo: Repository[Location]):
        self.repo = repo

    def _handle(self, query: GetLocationByIdQuery) -> dict:
        location = self.repo.get_by_id(query.location_id)
        if location is None:
            raise NotFoundError(f"Location {query.location_id} not found")
        return location.dict()
