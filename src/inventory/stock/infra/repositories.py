from src.inventory.stock.domain.entities import Stock
from src.inventory.stock.infra.models import StockModel
from src.shared.infra.repositories import BaseRepository


class StockRepositoryImpl(BaseRepository[Stock]):
    __model__ = StockModel
