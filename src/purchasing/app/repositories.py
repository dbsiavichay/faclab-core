from abc import abstractmethod

from src.purchasing.domain.entities import (
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseReceipt,
    PurchaseReceiptItem,
)
from src.shared.app.repositories import Repository


class PurchaseOrderRepository(Repository[PurchaseOrder]):
    @abstractmethod
    def count_by_year(self, year: int) -> int:
        raise NotImplementedError


class PurchaseOrderItemRepository(Repository[PurchaseOrderItem]):
    pass


class PurchaseReceiptRepository(Repository[PurchaseReceipt]):
    pass


class PurchaseReceiptItemRepository(Repository[PurchaseReceiptItem]):
    pass
