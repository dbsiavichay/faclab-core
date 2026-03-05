"""Admin routes for Sales (read-only)"""

from fastapi import APIRouter, Depends
from wireup import Injected

from src.sales.app.queries.get_payments import (
    GetSalePaymentsQuery,
    GetSalePaymentsQueryHandler,
)
from src.sales.app.queries.get_sale_items import (
    GetSaleItemsQuery,
    GetSaleItemsQueryHandler,
)
from src.sales.app.queries.get_sales import (
    GetAllSalesQuery,
    GetAllSalesQueryHandler,
    GetSaleByIdQuery,
    GetSaleByIdQueryHandler,
)
from src.sales.infra.validators import (
    PaymentResponse,
    SaleItemResponse,
    SaleQueryParams,
    SaleResponse,
)
from src.shared.infra.validators import PaginatedResponse


class SaleRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get(
            "",
            response_model=PaginatedResponse[SaleResponse],
            summary="List all sales",
        )(self.get_all_sales)
        self.router.get("/{sale_id}", response_model=SaleResponse, summary="Get sale")(
            self.get_sale
        )
        self.router.get(
            "/{sale_id}/items",
            response_model=list[SaleItemResponse],
            summary="List sale items",
        )(self.get_sale_items)
        self.router.get(
            "/{sale_id}/payments",
            response_model=list[PaymentResponse],
            summary="List sale payments",
        )(self.get_sale_payments)

    def get_all_sales(
        self,
        handler: Injected[GetAllSalesQueryHandler],
        query_params: SaleQueryParams = Depends(),
    ) -> PaginatedResponse[SaleResponse]:
        result = handler.handle(
            GetAllSalesQuery(**query_params.model_dump(exclude_none=True))
        )
        return PaginatedResponse[SaleResponse](
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            items=[SaleResponse.model_validate(r) for r in result["items"]],
        )

    def get_sale(
        self,
        handler: Injected[GetSaleByIdQueryHandler],
        sale_id: int,
    ) -> SaleResponse:
        result = handler.handle(GetSaleByIdQuery(sale_id=sale_id))
        return SaleResponse.model_validate(result)

    def get_sale_items(
        self,
        handler: Injected[GetSaleItemsQueryHandler],
        sale_id: int,
    ) -> list[SaleItemResponse]:
        result = handler.handle(GetSaleItemsQuery(sale_id=sale_id))
        return [SaleItemResponse.model_validate(r) for r in result]

    def get_sale_payments(
        self,
        handler: Injected[GetSalePaymentsQueryHandler],
        sale_id: int,
    ) -> list[PaymentResponse]:
        result = handler.handle(GetSalePaymentsQuery(sale_id=sale_id))
        return [PaymentResponse.model_validate(r) for r in result]
