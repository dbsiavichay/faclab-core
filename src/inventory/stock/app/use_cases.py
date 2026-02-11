
from src.inventory.stock.domain.entities import Stock
from src.shared.app.repositories import Repository

from .types import StockOutput


class FilterStocksUseCase:
    def __init__(self, repo: Repository[Stock]):
        self.repo = repo

    def execute(self, **params) -> list[StockOutput]:
        stocks = self.repo.filter_by(**params)
        return [stock.dict() for stock in stocks]
