from src.inventory.movement.domain.entities import Movement
from src.inventory.movement.infra.models import MovementModel
from src.shared.infra.repositories import BaseRepository


class MovementRepositoryImpl(BaseRepository[Movement]):
    __model__ = MovementModel
