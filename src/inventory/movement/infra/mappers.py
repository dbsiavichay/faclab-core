from wireup import injectable

from src.inventory.movement.domain.entities import Movement
from src.shared.infra.mappers import Mapper

from .models import MovementModel


@injectable
class MovementMapper(Mapper[Movement, MovementModel]):
    __entity__ = Movement
    __exclude_fields__ = frozenset({"created_at"})
