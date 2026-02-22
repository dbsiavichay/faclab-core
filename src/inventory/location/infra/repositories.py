from sqlalchemy.orm import Session
from wireup import injectable

from src.inventory.location.domain.entities import Location
from src.inventory.location.infra.mappers import LocationMapper
from src.inventory.location.infra.models import LocationModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=Repository[Location])
class LocationRepository(SqlAlchemyRepository[Location]):
    __model__ = LocationModel

    def __init__(self, session: Session, mapper: LocationMapper):
        super().__init__(session, mapper)
