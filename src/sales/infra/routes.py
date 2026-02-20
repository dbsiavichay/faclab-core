"""Routes para el módulo Sales"""

from fastapi import APIRouter, status
from wireup import Injected

from src.sales.app.commands.add_sale_item import (
    AddSaleItemCommand,
    AddSaleItemCommandHandler,
)
from src.sales.app.commands.cancel_sale import (
    CancelSaleCommand,
    CancelSaleCommandHandler,
)
from src.sales.app.commands.confirm_sale import (
    ConfirmSaleCommand,
    ConfirmSaleCommandHandler,
)
from src.sales.app.commands.create_sale import (
    CreateSaleCommand,
    CreateSaleCommandHandler,
)
from src.sales.app.commands.register_payment import (
    RegisterPaymentCommand,
    RegisterPaymentCommandHandler,
)
from src.sales.app.commands.remove_sale_item import (
    RemoveSaleItemCommand,
    RemoveSaleItemCommandHandler,
)
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
    CancelSaleRequest,
    PaymentRequest,
    PaymentResponse,
    SaleItemRequest,
    SaleItemResponse,
    SaleRequest,
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
        handler: Injected[CreateSaleCommandHandler],
        sale: SaleRequest,
    ) -> SaleResponse:
        """Create a new sale in DRAFT status"""
        result = handler.handle(CreateSaleCommand(**sale.model_dump(exclude_none=True)))
        return SaleResponse.model_validate(result)

    def get_all_sales(
        self,
        handler: Injected[GetAllSalesQueryHandler],
        customer_id: int | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SaleResponse]:
        """Get all sales with optional filters"""
        result = handler.handle(
            GetAllSalesQuery(
                customer_id=customer_id,
                status=status,
                limit=limit,
                offset=offset,
            )
        )
        return [SaleResponse.model_validate(r) for r in result]

    def get_sale(
        self,
        handler: Injected[GetSaleByIdQueryHandler],
        sale_id: int,
    ) -> SaleResponse:
        """Get a specific sale by ID"""
        result = handler.handle(GetSaleByIdQuery(sale_id=sale_id))
        return SaleResponse.model_validate(result)

    def add_sale_item(
        self,
        handler: Injected[AddSaleItemCommandHandler],
        sale_id: int,
        item: SaleItemRequest,
    ) -> SaleItemResponse:
        """Add a new item to a sale (only in DRAFT status)"""
        result = handler.handle(
            AddSaleItemCommand(sale_id=sale_id, **item.model_dump(exclude_none=True))
        )
        return SaleItemResponse.model_validate(result)

    def get_sale_items(
        self,
        handler: Injected[GetSaleItemsQueryHandler],
        sale_id: int,
    ) -> list[SaleItemResponse]:
        """Get all items of a sale"""
        result = handler.handle(GetSaleItemsQuery(sale_id=sale_id))
        return [SaleItemResponse.model_validate(r) for r in result]

    def remove_sale_item(
        self,
        handler: Injected[RemoveSaleItemCommandHandler],
        sale_id: int,
        item_id: int,
    ) -> dict:
        """Remove an item from a sale (only in DRAFT status)"""
        return handler.handle(
            RemoveSaleItemCommand(sale_id=sale_id, sale_item_id=item_id)
        )

    def confirm_sale(
        self,
        handler: Injected[ConfirmSaleCommandHandler],
        sale_id: int,
    ) -> SaleResponse:
        """
        Confirm a sale (only DRAFT sales can be confirmed).
        This will trigger inventory movements (OUT).
        """
        result = handler.handle(ConfirmSaleCommand(sale_id=sale_id))
        return SaleResponse.model_validate(result)

    def cancel_sale(
        self,
        handler: Injected[CancelSaleCommandHandler],
        sale_id: int,
        cancel_input: CancelSaleRequest | None = None,
    ) -> SaleResponse:
        """
        Cancel a sale (only DRAFT or CONFIRMED sales can be cancelled).
        If the sale was confirmed, this will trigger inventory reversal (IN movements).
        """
        reason = cancel_input.reason if cancel_input else None
        result = handler.handle(CancelSaleCommand(sale_id=sale_id, reason=reason))
        return SaleResponse.model_validate(result)

    def register_payment(
        self,
        handler: Injected[RegisterPaymentCommandHandler],
        sale_id: int,
        payment: PaymentRequest,
    ) -> PaymentResponse:
        """Register a payment for a sale"""
        result = handler.handle(
            RegisterPaymentCommand(
                sale_id=sale_id, **payment.model_dump(exclude_none=True)
            )
        )
        return PaymentResponse.model_validate(result)

    def get_sale_payments(
        self,
        handler: Injected[GetSalePaymentsQueryHandler],
        sale_id: int,
    ) -> list[PaymentResponse]:
        """Get all payments for a sale"""
        result = handler.handle(GetSalePaymentsQuery(sale_id=sale_id))
        return [PaymentResponse.model_validate(r) for r in result]
