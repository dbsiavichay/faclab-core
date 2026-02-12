from dataclasses import dataclass

from src.inventory.stock.app.types import StockOutput
from src.inventory.stock.domain.entities import Stock
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetAllStocksQuery(Query):
    """Query para obtener todos los stocks con filtros opcionales"""

    product_id: int | None = None


class GetAllStocksQueryHandler(QueryHandler[GetAllStocksQuery, list[StockOutput]]):
    def __init__(self, repo: Repository[Stock]):
        self.repo = repo

    def handle(self, query: GetAllStocksQuery) -> list[StockOutput]:
        if query.product_id is not None:
            stocks = self.repo.filter_by(product_id=query.product_id)
        else:
            stocks = self.repo.get_all()
        return [stock.dict() for stock in stocks]


@dataclass
class GetStockByIdQuery(Query):
    """Query para obtener un stock por su ID"""

    id: int = 0


class GetStockByIdQueryHandler(
    QueryHandler[GetStockByIdQuery, StockOutput | None]
):
    def __init__(self, repo: Repository[Stock]):
        self.repo = repo

    def handle(self, query: GetStockByIdQuery) -> StockOutput | None:
        stock = self.repo.get_by_id(query.id)
        if stock is None:
            return None
        return stock.dict()


@dataclass
class GetStockByProductQuery(Query):
    """Query para obtener el stock de un producto específico"""

    product_id: int = 0


class GetStockByProductQueryHandler(
    QueryHandler[GetStockByProductQuery, StockOutput | None]
):
    def __init__(self, repo: Repository[Stock]):
        self.repo = repo

    def handle(self, query: GetStockByProductQuery) -> StockOutput | None:
        stock = self.repo.first(product_id=query.product_id)
        if stock is None:
            return None
        return stock.dict()
