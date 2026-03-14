from src.pos.sales.app.commands import (
    POSCancelSaleCommandHandler,
    POSConfirmSaleCommandHandler,
    POSParkSaleCommandHandler,
    POSResumeSaleCommandHandler,
)
from src.pos.sales.app.commands.apply_discount import ApplySaleDiscountCommandHandler
from src.pos.sales.app.commands.create_sale import POSCreateSaleCommandHandler
from src.pos.sales.app.commands.quick_sale import QuickSaleCommandHandler
from src.pos.sales.app.queries.get_parked_sales import GetParkedSalesQueryHandler

INJECTABLES = [
    POSConfirmSaleCommandHandler,
    POSCancelSaleCommandHandler,
    POSCreateSaleCommandHandler,
    POSParkSaleCommandHandler,
    POSResumeSaleCommandHandler,
    ApplySaleDiscountCommandHandler,
    QuickSaleCommandHandler,
    GetParkedSalesQueryHandler,
]
