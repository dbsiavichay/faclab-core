"""Controllers para el módulo Sales"""

from wireup import injectable

from src.sales.app.commands import (
    AddSaleItemCommand,
    AddSaleItemCommandHandler,
    CancelSaleCommand,
    CancelSaleCommandHandler,
    ConfirmSaleCommand,
    ConfirmSaleCommandHandler,
    CreateSaleCommand,
    CreateSaleCommandHandler,
    RegisterPaymentCommand,
    RegisterPaymentCommandHandler,
    RemoveSaleItemCommand,
    RemoveSaleItemCommandHandler,
)
from src.sales.app.queries import (
    GetAllSalesQuery,
    GetAllSalesQueryHandler,
    GetSaleByIdQuery,
    GetSaleByIdQueryHandler,
    GetSaleItemsQuery,
    GetSaleItemsQueryHandler,
    GetSalePaymentsQuery,
    GetSalePaymentsQueryHandler,
)
from src.sales.infra.validators import (
    CancelSaleInput,
    PaymentInput,
    PaymentResponse,
    SaleInput,
    SaleItemInput,
    SaleItemResponse,
    SaleResponse,
)
from src.shared.infra.exceptions import NotFoundException


@injectable(lifetime="scoped")
class SaleController:
    """Controller para manejar las operaciones de ventas"""

    def __init__(
        self,
        # Command Handlers
        create_handler: CreateSaleCommandHandler,
        add_item_handler: AddSaleItemCommandHandler,
        remove_item_handler: RemoveSaleItemCommandHandler,
        confirm_handler: ConfirmSaleCommandHandler,
        cancel_handler: CancelSaleCommandHandler,
        register_payment_handler: RegisterPaymentCommandHandler,
        # Query Handlers
        get_all_handler: GetAllSalesQueryHandler,
        get_by_id_handler: GetSaleByIdQueryHandler,
        get_items_handler: GetSaleItemsQueryHandler,
        get_payments_handler: GetSalePaymentsQueryHandler,
    ):
        self.create_handler = create_handler
        self.add_item_handler = add_item_handler
        self.remove_item_handler = remove_item_handler
        self.confirm_handler = confirm_handler
        self.cancel_handler = cancel_handler
        self.register_payment_handler = register_payment_handler
        self.get_all_handler = get_all_handler
        self.get_by_id_handler = get_by_id_handler
        self.get_items_handler = get_items_handler
        self.get_payments_handler = get_payments_handler

    def create(self, request: SaleInput) -> SaleResponse:
        """Crea una nueva venta"""
        command = CreateSaleCommand(**request.model_dump(exclude_none=True))
        result = self.create_handler.handle(command)
        return SaleResponse.model_validate(result)

    def get_all(
        self,
        customer_id: int | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SaleResponse]:
        """Obtiene todas las ventas con filtros opcionales"""
        query = GetAllSalesQuery(
            customer_id=customer_id,
            status=status,
            limit=limit,
            offset=offset,
        )
        results = self.get_all_handler.handle(query)
        return [SaleResponse.model_validate(r) for r in results]

    def get_by_id(self, sale_id: int) -> SaleResponse:
        """Obtiene una venta por ID"""
        query = GetSaleByIdQuery(sale_id=sale_id)
        result = self.get_by_id_handler.handle(query)
        if not result:
            raise NotFoundException(f"Sale with id {sale_id} not found")
        return SaleResponse.model_validate(result)

    def add_item(self, sale_id: int, request: SaleItemInput) -> SaleItemResponse:
        """Agrega un item a una venta"""
        command = AddSaleItemCommand(
            sale_id=sale_id,
            **request.model_dump(exclude_none=True),
        )
        result = self.add_item_handler.handle(command)
        return SaleItemResponse.model_validate(result)

    def remove_item(self, sale_id: int, item_id: int) -> dict:
        """Elimina un item de una venta"""
        command = RemoveSaleItemCommand(sale_id=sale_id, sale_item_id=item_id)
        result = self.remove_item_handler.handle(command)
        return result

    def get_items(self, sale_id: int) -> list[SaleItemResponse]:
        """Obtiene los items de una venta"""
        query = GetSaleItemsQuery(sale_id=sale_id)
        results = self.get_items_handler.handle(query)
        return [SaleItemResponse.model_validate(r) for r in results]

    def confirm(self, sale_id: int) -> SaleResponse:
        """Confirma una venta (genera movimientos de inventario)"""
        command = ConfirmSaleCommand(sale_id=sale_id)
        result = self.confirm_handler.handle(command)
        return SaleResponse.model_validate(result)

    def cancel(
        self, sale_id: int, request: CancelSaleInput | None = None
    ) -> SaleResponse:
        """Cancela una venta (revierte movimientos si estaba confirmada)"""
        reason = request.reason if request else None
        command = CancelSaleCommand(sale_id=sale_id, reason=reason)
        result = self.cancel_handler.handle(command)
        return SaleResponse.model_validate(result)

    def register_payment(self, sale_id: int, request: PaymentInput) -> PaymentResponse:
        """Registra un pago para una venta"""
        command = RegisterPaymentCommand(
            sale_id=sale_id,
            **request.model_dump(exclude_none=True),
        )
        result = self.register_payment_handler.handle(command)
        return PaymentResponse.model_validate(result)

    def get_payments(self, sale_id: int) -> list[PaymentResponse]:
        """Obtiene los pagos de una venta"""
        query = GetSalePaymentsQuery(sale_id=sale_id)
        results = self.get_payments_handler.handle(query)
        return [PaymentResponse.model_validate(r) for r in results]
