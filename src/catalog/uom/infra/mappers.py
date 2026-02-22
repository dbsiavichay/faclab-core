from wireup import injectable

from src.catalog.uom.domain.entities import UnitOfMeasure
from src.catalog.uom.infra.models import UnitOfMeasureModel
from src.shared.infra.mappers import Mapper


@injectable
class UnitOfMeasureMapper(Mapper[UnitOfMeasure, UnitOfMeasureModel]):
    __entity__ = UnitOfMeasure
