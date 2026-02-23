from typing import Any

from src.inventory.adjustment.domain.entities import (
    AdjustmentStatus,
    InventoryAdjustment,
)
from src.shared.domain.specifications import Specification


class AdjustmentsByStatus(Specification):
    def __init__(self, status: AdjustmentStatus):
        self.status = status

    def is_satisfied_by(self, candidate: InventoryAdjustment) -> bool:
        return candidate.status == self.status

    def to_sql_criteria(self) -> list[Any]:
        from src.inventory.adjustment.infra.models import InventoryAdjustmentModel

        return [InventoryAdjustmentModel.status == self.status.value]


class AdjustmentsByWarehouse(Specification):
    def __init__(self, warehouse_id: int):
        self.warehouse_id = warehouse_id

    def is_satisfied_by(self, candidate: InventoryAdjustment) -> bool:
        return candidate.warehouse_id == self.warehouse_id

    def to_sql_criteria(self) -> list[Any]:
        from src.inventory.adjustment.infra.models import InventoryAdjustmentModel

        return [InventoryAdjustmentModel.warehouse_id == self.warehouse_id]
