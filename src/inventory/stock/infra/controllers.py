from typing import List

from src.inventory.stock.app.use_cases import FilterStocksUseCase
from src.inventory.stock.infra.validators import StockQueryParams, StockResponse


class StockController:
    def __init__(self, filter: FilterStocksUseCase):
        self.filter = filter

    def get_all(self, query_params: StockQueryParams) -> List[StockResponse]:
        stocks = self.filter.execute(**query_params.model_dump(exclude_none=True))
        return [StockResponse.model_validate(stock) for stock in stocks]
