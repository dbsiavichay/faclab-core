from wireup import injectable

from src.pos.cash.domain.entities import CashMovement
from src.pos.cash.infra.models import CashMovementModel
from src.shared.infra.mappers import Mapper


@injectable
class CashMovementMapper(Mapper[CashMovement, CashMovementModel]):
    __entity__ = CashMovement
