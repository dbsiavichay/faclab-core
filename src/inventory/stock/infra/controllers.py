from wireup import injectable

from src.inventory.stock.app.queries import (
    GetAllStocksQuery,
    GetAllStocksQueryHandler,
    GetStockByIdQuery,
    GetStockByIdQueryHandler,
    GetStockByProductQuery,
    GetStockByProductQueryHandler,
)
from src.inventory.stock.infra.validators import StockQueryParams, StockResponse
from src.shared.infra.exceptions import NotFoundException


@injectable(lifetime="scoped")
class StockController:
    def __init__(
        self,
        get_all_handler: GetAllStocksQueryHandler,
        get_by_id_handler: GetStockByIdQueryHandler,
        get_by_product_handler: GetStockByProductQueryHandler,
    ):
        self.get_all_handler = get_all_handler
        self.get_by_id_handler = get_by_id_handler
        self.get_by_product_handler = get_by_product_handler

    def get_all(self, query_params: StockQueryParams) -> list[StockResponse]:
        query = GetAllStocksQuery(**query_params.model_dump(exclude_none=True))
        stocks = self.get_all_handler.handle(query)
        return [StockResponse.model_validate(stock) for stock in stocks]

    def get_by_id(self, id: int) -> StockResponse:
        stock = self.get_by_id_handler.handle(GetStockByIdQuery(id=id))
        if stock is None:
            raise NotFoundException("Stock not found")
        return StockResponse.model_validate(stock)

    def get_by_product(self, product_id: int) -> StockResponse:
        stock = self.get_by_product_handler.handle(
            GetStockByProductQuery(product_id=product_id)
        )
        if stock is None:
            raise NotFoundException(f"Stock for product_id {product_id} not found")
        return StockResponse.model_validate(stock)
