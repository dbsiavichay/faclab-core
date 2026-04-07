from src.purchasing.app.commands.purchase_order import (
    CancelPurchaseOrderCommandHandler,
    CreatePurchaseOrderCommandHandler,
    DeletePurchaseOrderCommandHandler,
    SendPurchaseOrderCommandHandler,
    UpdatePurchaseOrderCommandHandler,
)
from src.purchasing.app.commands.purchase_order_item import (
    AddPurchaseOrderItemCommandHandler,
    RemovePurchaseOrderItemCommandHandler,
    UpdatePurchaseOrderItemCommandHandler,
)
from src.purchasing.app.commands.purchase_receipt import (
    CreatePurchaseReceiptCommandHandler,
)
from src.purchasing.app.queries.purchase_order import (
    GetAllPurchaseOrdersQueryHandler,
    GetPurchaseOrderByIdQueryHandler,
)
from src.purchasing.app.queries.purchase_order_item import (
    GetPurchaseOrderItemsByPOQueryHandler,
)
from src.purchasing.app.queries.purchase_receipt import (
    GetReceiptsByPurchaseOrderQueryHandler,
)
from src.purchasing.infra.mappers import (
    PurchaseOrderItemMapper,
    PurchaseOrderMapper,
    PurchaseReceiptItemMapper,
    PurchaseReceiptMapper,
)
from src.purchasing.infra.repositories import (
    SqlAlchemyPurchaseOrderItemRepository,
    SqlAlchemyPurchaseOrderRepository,
    SqlAlchemyPurchaseReceiptItemRepository,
    SqlAlchemyPurchaseReceiptRepository,
)

INJECTABLES = [
    PurchaseOrderMapper,
    PurchaseOrderItemMapper,
    PurchaseReceiptMapper,
    PurchaseReceiptItemMapper,
    SqlAlchemyPurchaseOrderRepository,
    SqlAlchemyPurchaseOrderItemRepository,
    SqlAlchemyPurchaseReceiptRepository,
    SqlAlchemyPurchaseReceiptItemRepository,
    CreatePurchaseOrderCommandHandler,
    UpdatePurchaseOrderCommandHandler,
    DeletePurchaseOrderCommandHandler,
    SendPurchaseOrderCommandHandler,
    CancelPurchaseOrderCommandHandler,
    AddPurchaseOrderItemCommandHandler,
    UpdatePurchaseOrderItemCommandHandler,
    RemovePurchaseOrderItemCommandHandler,
    CreatePurchaseReceiptCommandHandler,
    GetAllPurchaseOrdersQueryHandler,
    GetPurchaseOrderByIdQueryHandler,
    GetPurchaseOrderItemsByPOQueryHandler,
    GetReceiptsByPurchaseOrderQueryHandler,
]
