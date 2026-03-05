from fastapi import APIRouter, Depends
from wireup import Injected

from src.reports.inventory.app.queries.movement_history import (
    GetMovementHistoryReportQuery,
    GetMovementHistoryReportQueryHandler,
)
from src.reports.inventory.app.queries.rotation import (
    GetProductRotationQuery,
    GetProductRotationQueryHandler,
)
from src.reports.inventory.app.queries.valuation import (
    GetInventoryValuationQuery,
    GetInventoryValuationQueryHandler,
)
from src.reports.inventory.app.queries.warehouse_summary import (
    GetWarehouseSummaryQuery,
    GetWarehouseSummaryQueryHandler,
)
from src.reports.inventory.infra.validators import (
    InventoryValuationResponse,
    MovementHistoryItemResponse,
    MovementHistoryQueryParams,
    ProductRotationResponse,
    RotationQueryParams,
    SummaryQueryParams,
    ValuationQueryParams,
    WarehouseSummaryResponse,
)
from src.shared.infra.dependencies import get_meta
from src.shared.infra.validators import (
    DataResponse,
    ListResponse,
    Meta,
    PaginatedDataResponse,
)


class ReportRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get(
            "/valuation",
            response_model=DataResponse[InventoryValuationResponse],
            summary="Inventory valuation report",
        )(self.valuation)
        self.router.get(
            "/rotation",
            response_model=ListResponse[ProductRotationResponse],
            summary="Product rotation report",
        )(self.rotation)
        self.router.get(
            "/movements",
            response_model=PaginatedDataResponse[MovementHistoryItemResponse],
            summary="Movement history report",
        )(self.movement_history)
        self.router.get(
            "/summary",
            response_model=ListResponse[WarehouseSummaryResponse],
            summary="Warehouse summary report",
        )(self.warehouse_summary)

    def valuation(
        self,
        handler: Injected[GetInventoryValuationQueryHandler],
        query_params: ValuationQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[InventoryValuationResponse]:
        """
        Returns current inventory valuation (quantity x purchase price per product).
        Optionally filtered by warehouse and as-of date.
        If `asOfDate` is provided, stock is reconstructed from movement history up to that date.
        """
        result = handler.handle(
            GetInventoryValuationQuery(
                warehouse_id=query_params.warehouse_id,
                as_of_date=query_params.as_of_date,
            )
        )
        return DataResponse(
            data=InventoryValuationResponse.model_validate(result), meta=meta
        )

    def rotation(
        self,
        handler: Injected[GetProductRotationQueryHandler],
        query_params: RotationQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[ProductRotationResponse]:
        """
        Returns product rotation metrics for a given date range:
        total IN/OUT movements, current stock, turnover rate, and days of stock.
        """
        result = handler.handle(
            GetProductRotationQuery(
                from_date=query_params.from_date,
                to_date=query_params.to_date,
                warehouse_id=query_params.warehouse_id,
            )
        )
        return ListResponse(
            data=[ProductRotationResponse.model_validate(r) for r in result],
            meta=meta,
        )

    def movement_history(
        self,
        handler: Injected[GetMovementHistoryReportQueryHandler],
        query_params: MovementHistoryQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> PaginatedDataResponse[MovementHistoryItemResponse]:
        """
        Returns a paginated list of inventory movements enriched with product details.
        Supports filtering by product, type, date range, and warehouse.
        """
        result = handler.handle(
            GetMovementHistoryReportQuery(**query_params.model_dump(exclude_none=True))
        )
        return PaginatedDataResponse(
            data=[
                MovementHistoryItemResponse.model_validate(item)
                for item in result["items"]
            ],
            meta=meta.with_pagination(
                total=result["total"],
                limit=result["limit"],
                offset=result["offset"],
            ),
        )

    def warehouse_summary(
        self,
        handler: Injected[GetWarehouseSummaryQueryHandler],
        query_params: SummaryQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[WarehouseSummaryResponse]:
        """
        Returns aggregated stock summary per warehouse:
        total products, quantities, reserved stock, and total value.
        """
        result = handler.handle(
            GetWarehouseSummaryQuery(warehouse_id=query_params.warehouse_id)
        )
        return ListResponse(
            data=[WarehouseSummaryResponse.model_validate(r) for r in result],
            meta=meta,
        )
