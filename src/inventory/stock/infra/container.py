from src.inventory.stock.app.queries.stock import (
    GetAllStocksQueryHandler,
    GetStockByIdQueryHandler,
    GetStockByProductQueryHandler,
)
from src.inventory.stock.infra.mappers import StockMapper
from src.inventory.stock.infra.repositories import SqlAlchemyStockRepository

INJECTABLES = [
    StockMapper,
    SqlAlchemyStockRepository,
    GetAllStocksQueryHandler,
    GetStockByIdQueryHandler,
    GetStockByProductQueryHandler,
]
