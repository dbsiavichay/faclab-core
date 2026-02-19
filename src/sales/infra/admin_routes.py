"""Admin routes for Sales (read-only)"""

from fastapi import APIRouter
from wireup import Injected

from src.sales.infra.controllers import SaleController
from src.sales.infra.validators import PaymentResponse, SaleItemResponse, SaleResponse


class AdminSaleRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get("", response_model=list[SaleResponse])(self.get_all_sales)
        self.router.get("/{sale_id}", response_model=SaleResponse)(self.get_sale)
        self.router.get("/{sale_id}/items", response_model=list[SaleItemResponse])(
            self.get_sale_items
        )
        self.router.get("/{sale_id}/payments", response_model=list[PaymentResponse])(
            self.get_sale_payments
        )

    def get_all_sales(
        self,
        controller: Injected[SaleController],
        customer_id: int | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SaleResponse]:
        return controller.get_all(
            customer_id=customer_id,
            status=status,
            limit=limit,
            offset=offset,
        )

    def get_sale(
        self,
        controller: Injected[SaleController],
        sale_id: int,
    ) -> SaleResponse:
        return controller.get_by_id(sale_id)

    def get_sale_items(
        self,
        controller: Injected[SaleController],
        sale_id: int,
    ) -> list[SaleItemResponse]:
        return controller.get_items(sale_id)

    def get_sale_payments(
        self,
        controller: Injected[SaleController],
        sale_id: int,
    ) -> list[PaymentResponse]:
        return controller.get_payments(sale_id)
