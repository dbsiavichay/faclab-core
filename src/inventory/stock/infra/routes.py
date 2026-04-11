from fastapi import APIRouter, Depends
from wireup import Injected

from src.inventory.stock.app.queries.stock import (
    GetAllStocksQuery,
    GetAllStocksQueryHandler,
)
from src.inventory.stock.infra.validators import StockQueryParams, StockResponse
from src.shared.infra.dependencies import get_meta
from src.shared.infra.validators import RESPONSES_LIST, Meta, PaginatedDataResponse


class StockRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Sets up all the routes for the router."""
        self.router.get(
            "",
            response_model=PaginatedDataResponse[StockResponse],
            summary="Get all stocks",
            responses=RESPONSES_LIST,
        )(self.get_all)

    def get_all(
        self,
        handler: Injected[GetAllStocksQueryHandler],
        query_params: StockQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> PaginatedDataResponse[StockResponse]:
        """List current stock levels per product and location. Supports filtering and pagination."""
        result = handler.handle(
            GetAllStocksQuery(**query_params.model_dump(exclude_none=True))
        )
        return PaginatedDataResponse(
            data=[StockResponse.model_validate(s) for s in result["items"]],
            meta=meta.with_pagination(
                total=result["total"],
                limit=result["limit"],
                offset=result["offset"],
            ),
        )
