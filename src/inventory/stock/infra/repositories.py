from sqlalchemy.orm import Session
from wireup import injectable

from src.inventory.stock.app.repositories import StockRepository
from src.inventory.stock.domain.entities import Stock
from src.inventory.stock.infra.mappers import StockMapper
from src.inventory.stock.infra.models import StockModel
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=StockRepository)
class SqlAlchemyStockRepository(SqlAlchemyRepository[Stock], StockRepository):
    __model__ = StockModel

    def __init__(self, session: Session, mapper: StockMapper):
        super().__init__(session, mapper)
