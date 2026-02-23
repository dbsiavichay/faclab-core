from wireup import injectable

from src.purchasing.domain.entities import (
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseReceipt,
    PurchaseReceiptItem,
)
from src.purchasing.infra.models import (
    PurchaseOrderItemModel,
    PurchaseOrderModel,
    PurchaseReceiptItemModel,
    PurchaseReceiptModel,
)
from src.shared.infra.mappers import Mapper


@injectable
class PurchaseOrderMapper(Mapper[PurchaseOrder, PurchaseOrderModel]):
    __entity__ = PurchaseOrder
    __exclude_fields__ = frozenset({"created_at", "updated_at"})


@injectable
class PurchaseOrderItemMapper(Mapper[PurchaseOrderItem, PurchaseOrderItemModel]):
    __entity__ = PurchaseOrderItem


@injectable
class PurchaseReceiptMapper(Mapper[PurchaseReceipt, PurchaseReceiptModel]):
    __entity__ = PurchaseReceipt
    __exclude_fields__ = frozenset({"created_at"})


@injectable
class PurchaseReceiptItemMapper(Mapper[PurchaseReceiptItem, PurchaseReceiptItemModel]):
    __entity__ = PurchaseReceiptItem
