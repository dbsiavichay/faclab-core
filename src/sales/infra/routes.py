"""Routes para el módulo Sales"""

from fastapi import APIRouter, status
from wireup import Injected

from src.sales.infra.controllers import SaleController
from src.sales.infra.validators import (
    CancelSaleInput,
    PaymentInput,
    PaymentResponse,
    SaleInput,
    SaleItemInput,
    SaleItemResponse,
    SaleResponse,
)


class SaleRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Configura todas las rutas del router"""
        self.router.post(
            "", response_model=SaleResponse, status_code=status.HTTP_201_CREATED
        )(self.create_sale)
        self.router.get("", response_model=list[SaleResponse])(self.get_all_sales)
        self.router.get("/{sale_id}", response_model=SaleResponse)(self.get_sale)
        self.router.post(
            "/{sale_id}/items",
            response_model=SaleItemResponse,
            status_code=status.HTTP_201_CREATED,
        )(self.add_sale_item)
        self.router.get("/{sale_id}/items", response_model=list[SaleItemResponse])(
            self.get_sale_items
        )
        self.router.delete("/{sale_id}/items/{item_id}")(self.remove_sale_item)
        self.router.post("/{sale_id}/confirm", response_model=SaleResponse)(
            self.confirm_sale
        )
        self.router.post("/{sale_id}/cancel", response_model=SaleResponse)(
            self.cancel_sale
        )
        self.router.post(
            "/{sale_id}/payments",
            response_model=PaymentResponse,
            status_code=status.HTTP_201_CREATED,
        )(self.register_payment)
        self.router.get("/{sale_id}/payments", response_model=list[PaymentResponse])(
            self.get_sale_payments
        )

    def create_sale(
        self,
        controller: Injected[SaleController],
        sale: SaleInput,
    ) -> SaleResponse:
        """Create a new sale in DRAFT status"""
        return controller.create(sale)

    def get_all_sales(
        self,
        controller: Injected[SaleController],
        customer_id: int | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SaleResponse]:
        """Get all sales with optional filters"""
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
        """Get a specific sale by ID"""
        return controller.get_by_id(sale_id)

    def add_sale_item(
        self,
        controller: Injected[SaleController],
        sale_id: int,
        item: SaleItemInput,
    ) -> SaleItemResponse:
        """Add a new item to a sale (only in DRAFT status)"""
        return controller.add_item(sale_id, item)

    def get_sale_items(
        self,
        controller: Injected[SaleController],
        sale_id: int,
    ) -> list[SaleItemResponse]:
        """Get all items of a sale"""
        return controller.get_items(sale_id)

    def remove_sale_item(
        self,
        controller: Injected[SaleController],
        sale_id: int,
        item_id: int,
    ) -> dict:
        """Remove an item from a sale (only in DRAFT status)"""
        return controller.remove_item(sale_id, item_id)

    def confirm_sale(
        self,
        controller: Injected[SaleController],
        sale_id: int,
    ) -> SaleResponse:
        """
        Confirm a sale (only DRAFT sales can be confirmed).
        This will trigger inventory movements (OUT).
        """
        return controller.confirm(sale_id)

    def cancel_sale(
        self,
        controller: Injected[SaleController],
        sale_id: int,
        cancel_input: CancelSaleInput | None = None,
    ) -> SaleResponse:
        """
        Cancel a sale (only DRAFT or CONFIRMED sales can be cancelled).
        If the sale was confirmed, this will trigger inventory reversal (IN movements).
        """
        return controller.cancel(sale_id, cancel_input)

    def register_payment(
        self,
        controller: Injected[SaleController],
        sale_id: int,
        payment: PaymentInput,
    ) -> PaymentResponse:
        """Register a payment for a sale"""
        return controller.register_payment(sale_id, payment)

    def get_sale_payments(
        self,
        controller: Injected[SaleController],
        sale_id: int,
    ) -> list[PaymentResponse]:
        """Get all payments for a sale"""
        return controller.get_payments(sale_id)
