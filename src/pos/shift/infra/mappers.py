from wireup import injectable

from src.pos.shift.domain.entities import Shift
from src.pos.shift.infra.models import ShiftModel
from src.shared.infra.mappers import Mapper


@injectable(lifetime="singleton")
class ShiftMapper(Mapper[Shift, ShiftModel]):
    __entity__ = Shift
