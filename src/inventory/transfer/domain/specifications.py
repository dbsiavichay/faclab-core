from typing import Any

from src.inventory.transfer.domain.entities import StockTransfer, TransferStatus
from src.shared.domain.specifications import Specification


class TransfersByStatus(Specification):
    def __init__(self, status: TransferStatus):
        self.status = status

    def is_satisfied_by(self, candidate: StockTransfer) -> bool:
        return candidate.status == self.status

    def to_sql_criteria(self) -> list[Any]:
        from src.inventory.transfer.infra.models import StockTransferModel

        return [StockTransferModel.status == self.status.value]


class TransfersBySourceLocation(Specification):
    def __init__(self, location_id: int):
        self.location_id = location_id

    def is_satisfied_by(self, candidate: StockTransfer) -> bool:
        return candidate.source_location_id == self.location_id

    def to_sql_criteria(self) -> list[Any]:
        from src.inventory.transfer.infra.models import StockTransferModel

        return [StockTransferModel.source_location_id == self.location_id]
