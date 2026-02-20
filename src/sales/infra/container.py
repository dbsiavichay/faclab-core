from src.sales.app.commands.add_sale_item import AddSaleItemCommandHandler
from src.sales.app.commands.cancel_sale import CancelSaleCommandHandler
from src.sales.app.commands.confirm_sale import ConfirmSaleCommandHandler
from src.sales.app.commands.create_sale import CreateSaleCommandHandler
from src.sales.app.commands.register_payment import RegisterPaymentCommandHandler
from src.sales.app.commands.remove_sale_item import RemoveSaleItemCommandHandler
from src.sales.app.queries.get_payments import GetSalePaymentsQueryHandler
from src.sales.app.queries.get_sale_items import GetSaleItemsQueryHandler
from src.sales.app.queries.get_sales import (
    GetAllSalesQueryHandler,
    GetSaleByIdQueryHandler,
)
from src.sales.infra.controllers import SaleController
from src.sales.infra.mappers import PaymentMapper, SaleItemMapper, SaleMapper
from src.sales.infra.repositories import (
    PaymentRepository,
    SaleItemRepository,
    SaleRepository,
)

INJECTABLES = [
    SaleMapper,
    SaleItemMapper,
    PaymentMapper,
    SaleRepository,
    SaleItemRepository,
    PaymentRepository,
    CreateSaleCommandHandler,
    AddSaleItemCommandHandler,
    RemoveSaleItemCommandHandler,
    ConfirmSaleCommandHandler,
    CancelSaleCommandHandler,
    RegisterPaymentCommandHandler,
    GetAllSalesQueryHandler,
    GetSaleByIdQueryHandler,
    GetSaleItemsQueryHandler,
    GetSalePaymentsQueryHandler,
    SaleController,
]
