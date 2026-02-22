from sqlalchemy.orm import Session
from wireup import injectable

from src.catalog.uom.domain.entities import UnitOfMeasure
from src.catalog.uom.infra.mappers import UnitOfMeasureMapper
from src.catalog.uom.infra.models import UnitOfMeasureModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=Repository[UnitOfMeasure])
class UnitOfMeasureRepository(SqlAlchemyRepository[UnitOfMeasure]):
    __model__ = UnitOfMeasureModel

    def __init__(self, session: Session, mapper: UnitOfMeasureMapper):
        super().__init__(session, mapper)
