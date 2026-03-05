from fastapi import APIRouter, Depends
from wireup import Injected

from src.inventory.stock.app.queries.stock import (
    GetAllStocksQuery,
    GetAllStocksQueryHandler,
)
from src.inventory.stock.infra.validators import StockQueryParams, StockResponse
from src.shared.infra.validators import PaginatedResponse


class StockRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Sets up all the routes for the router."""
        self.router.get(
            "",
            response_model=PaginatedResponse[StockResponse],
            summary="Get all stocks",
        )(self.get_all)

    def get_all(
        self,
        handler: Injected[GetAllStocksQueryHandler],
        query_params: StockQueryParams = Depends(),
    ) -> PaginatedResponse[StockResponse]:
        """Gets all products stock."""
        result = handler.handle(
            GetAllStocksQuery(**query_params.model_dump(exclude_none=True))
        )
        return PaginatedResponse[StockResponse](
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            items=[StockResponse.model_validate(s) for s in result["items"]],
        )
