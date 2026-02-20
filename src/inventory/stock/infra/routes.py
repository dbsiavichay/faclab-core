from fastapi import APIRouter, Depends
from wireup import Injected

from src.inventory.stock.app.queries.stock import (
    GetAllStocksQuery,
    GetAllStocksQueryHandler,
)
from src.inventory.stock.infra.validators import StockQueryParams, StockResponse


class StockRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Sets up all the routes for the router."""
        self.router.get(
            "", response_model=list[StockResponse], summary="Get all stocks"
        )(self.get_all)

    def get_all(
        self,
        handler: Injected[GetAllStocksQueryHandler],
        query_params: StockQueryParams = Depends(),
    ) -> list[StockResponse]:
        """Gets all products stock."""
        result = handler.handle(
            GetAllStocksQuery(**query_params.model_dump(exclude_none=True))
        )
        return [StockResponse.model_validate(s) for s in result]
