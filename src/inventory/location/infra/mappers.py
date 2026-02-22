from wireup import injectable

from src.inventory.location.domain.entities import Location
from src.inventory.location.infra.models import LocationModel
from src.shared.infra.mappers import Mapper


@injectable
class LocationMapper(Mapper[Location, LocationModel]):
    __entity__ = Location
