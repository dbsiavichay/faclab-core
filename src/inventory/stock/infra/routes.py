from fastapi import APIRouter, Depends
from wireup import Injected

from .controllers import StockController
from .validators import StockQueryParams, StockResponse


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
        controller: Injected[StockController],
        query_params: StockQueryParams = Depends(),
    ):
        """Gets all products stock."""
        return controller.get_all(query_params)
