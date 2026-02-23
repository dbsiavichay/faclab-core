"""POS sale routes"""

from fastapi import APIRouter, status
from wireup import Injected

from src.pos.sales.app.commands.cancel_sale import (
    POSCancelSaleCommand,
    POSCancelSaleCommandHandler,
)
from src.pos.sales.app.commands.confirm_sale import (
    POSConfirmSaleCommand,
    POSConfirmSaleCommandHandler,
)
from src.sales.app.commands.add_sale_item import (
    AddSaleItemCommand,
    AddSaleItemCommandHandler,
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
from src.sales.app.queries.get_sales import GetSaleByIdQuery, GetSaleByIdQueryHandler
from src.sales.infra.validators import (
    CancelSaleRequest,
    PaymentRequest,
    PaymentResponse,
    SaleItemRequest,
    SaleItemResponse,
    SaleRequest,
    SaleResponse,
)


class POSSaleRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=SaleResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create sale",
        )(self.create_sale)
        self.router.get("/{sale_id}", response_model=SaleResponse, summary="Get sale")(
            self.get_sale
        )
        self.router.post(
            "/{sale_id}/items",
            response_model=SaleItemResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Add item to sale",
        )(self.add_sale_item)
        self.router.get(
            "/{sale_id}/items",
            response_model=list[SaleItemResponse],
            summary="List sale items",
        )(self.get_sale_items)
        self.router.delete(
            "/{sale_id}/items/{item_id}", summary="Remove item from sale"
        )(self.remove_sale_item)
        self.router.post(
            "/{sale_id}/confirm", response_model=SaleResponse, summary="Confirm sale"
        )(self.confirm_sale)
        self.router.post(
            "/{sale_id}/cancel", response_model=SaleResponse, summary="Cancel sale"
        )(self.cancel_sale)
        self.router.post(
            "/{sale_id}/payments",
            response_model=PaymentResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Register payment",
        )(self.register_payment)
        self.router.get(
            "/{sale_id}/payments",
            response_model=list[PaymentResponse],
            summary="List sale payments",
        )(self.get_sale_payments)

    def create_sale(
        self,
        handler: Injected[CreateSaleCommandHandler],
        sale: SaleRequest,
    ) -> SaleResponse:
        result = handler.handle(CreateSaleCommand(**sale.model_dump(exclude_none=True)))
        return SaleResponse.model_validate(result)

    def get_sale(
        self,
        handler: Injected[GetSaleByIdQueryHandler],
        sale_id: int,
    ) -> SaleResponse:
        result = handler.handle(GetSaleByIdQuery(sale_id=sale_id))
        return SaleResponse.model_validate(result)

    def add_sale_item(
        self,
        handler: Injected[AddSaleItemCommandHandler],
        sale_id: int,
        item: SaleItemRequest,
    ) -> SaleItemResponse:
        result = handler.handle(
            AddSaleItemCommand(sale_id=sale_id, **item.model_dump(exclude_none=True))
        )
        return SaleItemResponse.model_validate(result)

    def get_sale_items(
        self,
        handler: Injected[GetSaleItemsQueryHandler],
        sale_id: int,
    ) -> list[SaleItemResponse]:
        result = handler.handle(GetSaleItemsQuery(sale_id=sale_id))
        return [SaleItemResponse.model_validate(r) for r in result]

    def remove_sale_item(
        self,
        handler: Injected[RemoveSaleItemCommandHandler],
        sale_id: int,
        item_id: int,
    ) -> dict:
        return handler.handle(
            RemoveSaleItemCommand(sale_id=sale_id, sale_item_id=item_id)
        )

    def confirm_sale(
        self,
        handler: Injected[POSConfirmSaleCommandHandler],
        sale_id: int,
    ) -> SaleResponse:
        result = handler.handle(POSConfirmSaleCommand(sale_id=sale_id))
        return SaleResponse.model_validate(result)

    def cancel_sale(
        self,
        handler: Injected[POSCancelSaleCommandHandler],
        sale_id: int,
        cancel_input: CancelSaleRequest | None = None,
    ) -> SaleResponse:
        reason = cancel_input.reason if cancel_input else None
        result = handler.handle(POSCancelSaleCommand(sale_id=sale_id, reason=reason))
        return SaleResponse.model_validate(result)

    def register_payment(
        self,
        handler: Injected[RegisterPaymentCommandHandler],
        sale_id: int,
        payment: PaymentRequest,
    ) -> PaymentResponse:
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
        result = handler.handle(GetSalePaymentsQuery(sale_id=sale_id))
        return [PaymentResponse.model_validate(r) for r in result]
