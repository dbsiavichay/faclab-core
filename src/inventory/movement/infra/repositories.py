from sqlalchemy.orm import Session
from wireup import injectable

from src.inventory.movement.domain.entities import Movement
from src.inventory.movement.infra.mappers import MovementMapper
from src.inventory.movement.infra.models import MovementModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import BaseRepository


@injectable(lifetime="scoped")
class MovementRepositoryImpl(BaseRepository[Movement]):
    __model__ = MovementModel


@injectable(lifetime="scoped", as_type=Repository[Movement])
def create_movement_repository(
    session: Session, mapper: MovementMapper
) -> Repository[Movement]:
    """Factory function for creating MovementRepository with generic type binding.

    Args:
        session: Scoped database session
        mapper: MovementMapper instance

    Returns:
        Repository[Movement]: Movement repository implementation
    """
    return MovementRepositoryImpl(session, mapper)
