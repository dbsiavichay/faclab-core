from sqlalchemy.orm import Session
from wireup import injectable

from src.inventory.movement.app.repositories import MovementRepository
from src.inventory.movement.domain.entities import Movement
from src.inventory.movement.infra.mappers import MovementMapper
from src.inventory.movement.infra.models import MovementModel
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=MovementRepository)
class SqlAlchemyMovementRepository(SqlAlchemyRepository[Movement], MovementRepository):
    __model__ = MovementModel

    def __init__(self, session: Session, mapper: MovementMapper):
        super().__init__(session, mapper)
