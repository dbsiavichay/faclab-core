from src.inventory.transfer.app.commands.transfer import (
    AddTransferItemCommandHandler,
    CancelStockTransferCommandHandler,
    ConfirmStockTransferCommandHandler,
    CreateStockTransferCommandHandler,
    DeleteStockTransferCommandHandler,
    ReceiveStockTransferCommandHandler,
    RemoveTransferItemCommandHandler,
    UpdateStockTransferCommandHandler,
    UpdateTransferItemCommandHandler,
)
from src.inventory.transfer.app.queries.transfer import (
    GetAllTransfersQueryHandler,
    GetTransferByIdQueryHandler,
    GetTransferItemsQueryHandler,
)
from src.inventory.transfer.infra.mappers import (
    StockTransferItemMapper,
    StockTransferMapper,
)
from src.inventory.transfer.infra.repositories import (
    SqlAlchemyStockTransferItemRepository,
    SqlAlchemyStockTransferRepository,
)

TRANSFER_INJECTABLES = [
    StockTransferMapper,
    StockTransferItemMapper,
    SqlAlchemyStockTransferRepository,
    SqlAlchemyStockTransferItemRepository,
    CreateStockTransferCommandHandler,
    UpdateStockTransferCommandHandler,
    DeleteStockTransferCommandHandler,
    ConfirmStockTransferCommandHandler,
    ReceiveStockTransferCommandHandler,
    CancelStockTransferCommandHandler,
    AddTransferItemCommandHandler,
    UpdateTransferItemCommandHandler,
    RemoveTransferItemCommandHandler,
    GetAllTransfersQueryHandler,
    GetTransferByIdQueryHandler,
    GetTransferItemsQueryHandler,
]
