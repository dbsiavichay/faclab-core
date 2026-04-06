from wireup import injectable

from src.inventory.lot.domain.entities import Lot, MovementLotItem
from src.inventory.lot.infra.models import LotModel, MovementLotItemModel
from src.shared.infra.mappers import Mapper


@injectable(lifetime="singleton")
class LotMapper(Mapper[Lot, LotModel]):
    __entity__ = Lot
    __exclude_fields__ = frozenset({"created_at"})


@injectable(lifetime="singleton")
class MovementLotItemMapper(Mapper[MovementLotItem, MovementLotItemModel]):
    __entity__ = MovementLotItem
