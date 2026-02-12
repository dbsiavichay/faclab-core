from sqlalchemy.orm import Session
from wireup import injectable

from src.inventory.stock.domain.entities import Stock
from src.inventory.stock.infra.mappers import StockMapper
from src.inventory.stock.infra.models import StockModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import BaseRepository


@injectable(lifetime="scoped")
class StockRepositoryImpl(BaseRepository[Stock]):
    __model__ = StockModel


@injectable(lifetime="scoped", as_type=Repository[Stock])
def create_stock_repository(
    session: Session, mapper: StockMapper
) -> Repository[Stock]:
    """Factory function for creating StockRepository with generic type binding.

    Args:
        session: Scoped database session
        mapper: StockMapper instance

    Returns:
        Repository[Stock]: Stock repository implementation
    """
    return StockRepositoryImpl(session, mapper)
