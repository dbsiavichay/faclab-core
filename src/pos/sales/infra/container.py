from src.pos.sales.app.commands import (
    POSCancelSaleCommandHandler,
    POSConfirmSaleCommandHandler,
)
from src.pos.sales.app.commands.create_sale import POSCreateSaleCommandHandler

INJECTABLES = [
    POSConfirmSaleCommandHandler,
    POSCancelSaleCommandHandler,
    POSCreateSaleCommandHandler,
]
