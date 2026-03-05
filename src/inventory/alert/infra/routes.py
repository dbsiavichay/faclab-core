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
from src.shared.infra.dependencies import get_meta
from src.shared.infra.validators import ListResponse, Meta


class AlertRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get(
            "/low-stock",
            response_model=ListResponse[StockAlertResponse],
            summary="Get low stock alerts",
        )(self.low_stock)
        self.router.get(
            "/out-of-stock",
            response_model=ListResponse[StockAlertResponse],
            summary="Get out of stock alerts",
        )(self.out_of_stock)
        self.router.get(
            "/reorder-point",
            response_model=ListResponse[StockAlertResponse],
            summary="Get reorder point alerts",
        )(self.reorder_point)
        self.router.get(
            "/expiring-lots",
            response_model=ListResponse[StockAlertResponse],
            summary="Get expiring lots alerts",
        )(self.expiring_lots)

    def low_stock(
        self,
        handler: Injected[GetLowStockAlertsQueryHandler],
        query_params: StockAlertQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[StockAlertResponse]:
        """Get alerts for products whose stock is at or below the minimum stock level."""
        result = handler.handle(
            GetLowStockAlertsQuery(
                **query_params.model_dump(exclude_none=True, by_alias=False)
            )
        )
        return ListResponse(
            data=[StockAlertResponse.model_validate(a) for a in result], meta=meta
        )

    def out_of_stock(
        self,
        handler: Injected[GetOutOfStockAlertsQueryHandler],
        query_params: StockAlertQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[StockAlertResponse]:
        """Get alerts for products with zero stock."""
        result = handler.handle(
            GetOutOfStockAlertsQuery(
                **query_params.model_dump(exclude_none=True, by_alias=False)
            )
        )
        return ListResponse(
            data=[StockAlertResponse.model_validate(a) for a in result], meta=meta
        )

    def reorder_point(
        self,
        handler: Injected[GetReorderPointAlertsQueryHandler],
        query_params: StockAlertQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[StockAlertResponse]:
        """Get alerts for products whose stock is at or below the reorder point."""
        result = handler.handle(
            GetReorderPointAlertsQuery(
                **query_params.model_dump(exclude_none=True, by_alias=False)
            )
        )
        return ListResponse(
            data=[StockAlertResponse.model_validate(a) for a in result], meta=meta
        )

    def expiring_lots(
        self,
        handler: Injected[GetExpiringLotsAlertsQueryHandler],
        query_params: ExpiringLotsQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[StockAlertResponse]:
        """Get alerts for lots expiring within the specified number of days."""
        result = handler.handle(
            GetExpiringLotsAlertsQuery(**query_params.model_dump(by_alias=False))
        )
        return ListResponse(
            data=[StockAlertResponse.model_validate(a) for a in result], meta=meta
        )
