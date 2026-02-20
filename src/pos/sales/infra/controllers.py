"""POS Sale controller"""

from wireup import injectable

from src.pos.sales.app.commands import (
    POSCancelSaleCommand,
    POSCancelSaleCommandHandler,
    POSConfirmSaleCommand,
    POSConfirmSaleCommandHandler,
)
from src.sales.app.commands import (
    AddSaleItemCommand,
    AddSaleItemCommandHandler,
    CreateSaleCommand,
    CreateSaleCommandHandler,
    RegisterPaymentCommand,
    RegisterPaymentCommandHandler,
    RemoveSaleItemCommand,
    RemoveSaleItemCommandHandler,
)
from src.sales.app.queries import (
    GetSaleByIdQuery,
    GetSaleByIdQueryHandler,
    GetSaleItemsQuery,
    GetSaleItemsQueryHandler,
    GetSalePaymentsQuery,
    GetSalePaymentsQueryHandler,
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
from src.shared.infra.exceptions import NotFoundError


@injectable(lifetime="scoped")
class POSSaleController:
    def __init__(
        self,
        create_handler: CreateSaleCommandHandler,
        add_item_handler: AddSaleItemCommandHandler,
        remove_item_handler: RemoveSaleItemCommandHandler,
        register_payment_handler: RegisterPaymentCommandHandler,
        get_by_id_handler: GetSaleByIdQueryHandler,
        get_items_handler: GetSaleItemsQueryHandler,
        get_payments_handler: GetSalePaymentsQueryHandler,
        confirm_handler: POSConfirmSaleCommandHandler,
        cancel_handler: POSCancelSaleCommandHandler,
    ):
        self.create_handler = create_handler
        self.add_item_handler = add_item_handler
        self.remove_item_handler = remove_item_handler
        self.register_payment_handler = register_payment_handler
        self.get_by_id_handler = get_by_id_handler
        self.get_items_handler = get_items_handler
        self.get_payments_handler = get_payments_handler
        self.confirm_handler = confirm_handler
        self.cancel_handler = cancel_handler

    def create(self, request: SaleRequest) -> SaleResponse:
        command = CreateSaleCommand(**request.model_dump(exclude_none=True))
        result = self.create_handler.handle(command)
        return SaleResponse.model_validate(result)

    def get_by_id(self, sale_id: int) -> SaleResponse:
        query = GetSaleByIdQuery(sale_id=sale_id)
        result = self.get_by_id_handler.handle(query)
        if not result:
            raise NotFoundError(f"Sale with id {sale_id} not found")
        return SaleResponse.model_validate(result)

    def add_item(self, sale_id: int, request: SaleItemRequest) -> SaleItemResponse:
        command = AddSaleItemCommand(
            sale_id=sale_id,
            **request.model_dump(exclude_none=True),
        )
        result = self.add_item_handler.handle(command)
        return SaleItemResponse.model_validate(result)

    def remove_item(self, sale_id: int, item_id: int) -> dict:
        command = RemoveSaleItemCommand(sale_id=sale_id, sale_item_id=item_id)
        return self.remove_item_handler.handle(command)

    def get_items(self, sale_id: int) -> list[SaleItemResponse]:
        query = GetSaleItemsQuery(sale_id=sale_id)
        results = self.get_items_handler.handle(query)
        return [SaleItemResponse.model_validate(r) for r in results]

    def confirm(self, sale_id: int) -> SaleResponse:
        command = POSConfirmSaleCommand(sale_id=sale_id)
        result = self.confirm_handler.handle(command)
        return SaleResponse.model_validate(result)

    def cancel(
        self, sale_id: int, request: CancelSaleRequest | None = None
    ) -> SaleResponse:
        reason = request.reason if request else None
        command = POSCancelSaleCommand(sale_id=sale_id, reason=reason)
        result = self.cancel_handler.handle(command)
        return SaleResponse.model_validate(result)

    def register_payment(
        self, sale_id: int, request: PaymentRequest
    ) -> PaymentResponse:
        command = RegisterPaymentCommand(
            sale_id=sale_id,
            **request.model_dump(exclude_none=True),
        )
        result = self.register_payment_handler.handle(command)
        return PaymentResponse.model_validate(result)

    def get_payments(self, sale_id: int) -> list[PaymentResponse]:
        query = GetSalePaymentsQuery(sale_id=sale_id)
        results = self.get_payments_handler.handle(query)
        return [PaymentResponse.model_validate(r) for r in results]
