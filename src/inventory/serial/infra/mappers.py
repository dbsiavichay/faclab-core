from wireup import injectable

from src.inventory.serial.domain.entities import SerialNumber
from src.inventory.serial.infra.models import SerialNumberModel
from src.shared.infra.mappers import Mapper


@injectable
class SerialNumberMapper(Mapper[SerialNumber, SerialNumberModel]):
    __entity__ = SerialNumber
    __exclude_fields__ = frozenset({"created_at"})
