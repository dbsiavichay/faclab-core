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
    StockTransferItemRepository,
    StockTransferRepository,
)

TRANSFER_INJECTABLES = [
    StockTransferMapper,
    StockTransferItemMapper,
    StockTransferRepository,
    StockTransferItemRepository,
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
