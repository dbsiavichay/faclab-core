from src.inventory.transfer.domain.entities import StockTransfer, StockTransferItem
from src.shared.app.repositories import Repository


class StockTransferRepository(Repository[StockTransfer]):
    pass


class StockTransferItemRepository(Repository[StockTransferItem]):
    pass
