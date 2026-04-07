from sqlalchemy.orm import Session
from wireup import injectable

from src.catalog.uom.app.repositories import UnitOfMeasureRepository
from src.catalog.uom.domain.entities import UnitOfMeasure
from src.catalog.uom.infra.mappers import UnitOfMeasureMapper
from src.catalog.uom.infra.models import UnitOfMeasureModel
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=UnitOfMeasureRepository)
class SqlAlchemyUnitOfMeasureRepository(
    SqlAlchemyRepository[UnitOfMeasure], UnitOfMeasureRepository
):
    __model__ = UnitOfMeasureModel

    def __init__(self, session: Session, mapper: UnitOfMeasureMapper):
        super().__init__(session, mapper)
