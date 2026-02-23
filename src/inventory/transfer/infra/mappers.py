from wireup import injectable

from src.inventory.transfer.domain.entities import StockTransfer, StockTransferItem
from src.shared.infra.mappers import Mapper

from .models import StockTransferItemModel, StockTransferModel


@injectable
class StockTransferMapper(Mapper[StockTransfer, StockTransferModel]):
    __entity__ = StockTransfer
    __exclude_fields__ = frozenset({"created_at"})


@injectable
class StockTransferItemMapper(Mapper[StockTransferItem, StockTransferItemModel]):
    __entity__ = StockTransferItem
