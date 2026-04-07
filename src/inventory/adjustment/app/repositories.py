from src.inventory.adjustment.domain.entities import AdjustmentItem, InventoryAdjustment
from src.shared.app.repositories import Repository


class InventoryAdjustmentRepository(Repository[InventoryAdjustment]):
    pass


class AdjustmentItemRepository(Repository[AdjustmentItem]):
    pass
