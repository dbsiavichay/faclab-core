from sqlalchemy.orm import Session
from wireup import injectable

from src.pos.shift.domain.entities import Shift
from src.pos.shift.infra.mappers import ShiftMapper
from src.pos.shift.infra.models import ShiftModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=Repository[Shift])
class ShiftRepository(SqlAlchemyRepository[Shift]):
    __model__ = ShiftModel

    def __init__(self, session: Session, mapper: ShiftMapper):
        super().__init__(session, mapper)
