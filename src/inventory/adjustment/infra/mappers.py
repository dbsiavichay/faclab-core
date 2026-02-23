from wireup import injectable

from src.inventory.adjustment.domain.entities import AdjustmentItem, InventoryAdjustment
from src.shared.infra.mappers import Mapper

from .models import AdjustmentItemModel, InventoryAdjustmentModel


@injectable
class InventoryAdjustmentMapper(Mapper[InventoryAdjustment, InventoryAdjustmentModel]):
    __entity__ = InventoryAdjustment
    __exclude_fields__ = frozenset({"created_at"})


@injectable
class AdjustmentItemMapper(Mapper[AdjustmentItem, AdjustmentItemModel]):
    __entity__ = AdjustmentItem
