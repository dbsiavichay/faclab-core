from wireup import injectable

from src.inventory.warehouse.domain.entities import Warehouse
from src.inventory.warehouse.infra.models import WarehouseModel
from src.shared.infra.mappers import Mapper


@injectable
class WarehouseMapper(Mapper[Warehouse, WarehouseModel]):
    __entity__ = Warehouse
    __exclude_fields__ = frozenset({"created_at"})
