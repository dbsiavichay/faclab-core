from sqlalchemy.orm import Session
from wireup import injectable

from src.inventory.transfer.app.repositories import (
    StockTransferItemRepository,
    StockTransferRepository,
)
from src.inventory.transfer.domain.entities import StockTransfer, StockTransferItem
from src.inventory.transfer.infra.mappers import (
    StockTransferItemMapper,
    StockTransferMapper,
)
from src.inventory.transfer.infra.models import (
    StockTransferItemModel,
    StockTransferModel,
)
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=StockTransferRepository)
class SqlAlchemyStockTransferRepository(
    SqlAlchemyRepository[StockTransfer], StockTransferRepository
):
    __model__ = StockTransferModel

    def __init__(self, session: Session, mapper: StockTransferMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=StockTransferItemRepository)
class SqlAlchemyStockTransferItemRepository(
    SqlAlchemyRepository[StockTransferItem], StockTransferItemRepository
):
    __model__ = StockTransferItemModel

    def __init__(self, session: Session, mapper: StockTransferItemMapper):
        super().__init__(session, mapper)
