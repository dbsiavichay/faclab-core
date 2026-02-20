from src.inventory.stock.app.queries.stock import (
    GetAllStocksQueryHandler,
    GetStockByIdQueryHandler,
    GetStockByProductQueryHandler,
)
from src.inventory.stock.infra.controllers import StockController
from src.inventory.stock.infra.mappers import StockMapper
from src.inventory.stock.infra.repositories import StockRepository

INJECTABLES = [
    StockMapper,
    StockRepository,
    GetAllStocksQueryHandler,
    GetStockByIdQueryHandler,
    GetStockByProductQueryHandler,
    StockController,
]
