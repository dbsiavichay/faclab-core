from sqlalchemy.orm import Session
from wireup import injectable

from src.pos.cash.app.repositories import CashMovementRepository
from src.pos.cash.domain.entities import CashMovement
from src.pos.cash.infra.mappers import CashMovementMapper
from src.pos.cash.infra.models import CashMovementModel
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=CashMovementRepository)
class SqlAlchemyCashMovementRepository(
    SqlAlchemyRepository[CashMovement], CashMovementRepository
):
    __model__ = CashMovementModel

    def __init__(self, session: Session, mapper: CashMovementMapper):
        super().__init__(session, mapper)
