from sqlalchemy.orm import Session
from wireup import injectable

from src.inventory.transfer.domain.entities import StockTransfer, StockTransferItem
from src.inventory.transfer.infra.mappers import (
    StockTransferItemMapper,
    StockTransferMapper,
)
from src.inventory.transfer.infra.models import (
    StockTransferItemModel,
    StockTransferModel,
)
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=Repository[StockTransfer])
class StockTransferRepository(SqlAlchemyRepository[StockTransfer]):
    __model__ = StockTransferModel

    def __init__(self, session: Session, mapper: StockTransferMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=Repository[StockTransferItem])
class StockTransferItemRepository(SqlAlchemyRepository[StockTransferItem]):
    __model__ = StockTransferItemModel

    def __init__(self, session: Session, mapper: StockTransferItemMapper):
        super().__init__(session, mapper)
