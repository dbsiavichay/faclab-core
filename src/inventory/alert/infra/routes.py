from fastapi import APIRouter, Depends
from wireup import Injected

from src.inventory.alert.app.queries.alerts import (
    GetExpiringLotsAlertsQuery,
    GetExpiringLotsAlertsQueryHandler,
    GetLowStockAlertsQuery,
    GetLowStockAlertsQueryHandler,
    GetOutOfStockAlertsQuery,
    GetOutOfStockAlertsQueryHandler,
    GetReorderPointAlertsQuery,
    GetReorderPointAlertsQueryHandler,
)
from src.inventory.alert.infra.validators import (
    ExpiringLotsQueryParams,
    StockAlertQueryParams,
    StockAlertResponse,
)


class AlertRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get(
            "/low-stock",
            response_model=list[StockAlertResponse],
            summary="Get low stock alerts",
        )(self.low_stock)
        self.router.get(
            "/out-of-stock",
            response_model=list[StockAlertResponse],
            summary="Get out of stock alerts",
        )(self.out_of_stock)
        self.router.get(
            "/reorder-point",
            response_model=list[StockAlertResponse],
            summary="Get reorder point alerts",
        )(self.reorder_point)
        self.router.get(
            "/expiring-lots",
            response_model=list[StockAlertResponse],
            summary="Get expiring lots alerts",
        )(self.expiring_lots)

    def low_stock(
        self,
        handler: Injected[GetLowStockAlertsQueryHandler],
        query_params: StockAlertQueryParams = Depends(),
    ) -> list[StockAlertResponse]:
        """Get alerts for products whose stock is at or below the minimum stock level."""
        result = handler.handle(
            GetLowStockAlertsQuery(
                **query_params.model_dump(exclude_none=True, by_alias=False)
            )
        )
        return [StockAlertResponse.model_validate(a) for a in result]

    def out_of_stock(
        self,
        handler: Injected[GetOutOfStockAlertsQueryHandler],
        query_params: StockAlertQueryParams = Depends(),
    ) -> list[StockAlertResponse]:
        """Get alerts for products with zero stock."""
        result = handler.handle(
            GetOutOfStockAlertsQuery(
                **query_params.model_dump(exclude_none=True, by_alias=False)
            )
        )
        return [StockAlertResponse.model_validate(a) for a in result]

    def reorder_point(
        self,
        handler: Injected[GetReorderPointAlertsQueryHandler],
        query_params: StockAlertQueryParams = Depends(),
    ) -> list[StockAlertResponse]:
        """Get alerts for products whose stock is at or below the reorder point."""
        result = handler.handle(
            GetReorderPointAlertsQuery(
                **query_params.model_dump(exclude_none=True, by_alias=False)
            )
        )
        return [StockAlertResponse.model_validate(a) for a in result]

    def expiring_lots(
        self,
        handler: Injected[GetExpiringLotsAlertsQueryHandler],
        query_params: ExpiringLotsQueryParams = Depends(),
    ) -> list[StockAlertResponse]:
        """Get alerts for lots expiring within the specified number of days."""
        result = handler.handle(
            GetExpiringLotsAlertsQuery(**query_params.model_dump(by_alias=False))
        )
        return [StockAlertResponse.model_validate(a) for a in result]
