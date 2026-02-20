from src.pos.sales.app.commands import (
    POSCancelSaleCommandHandler,
    POSConfirmSaleCommandHandler,
)
from src.pos.sales.infra.controllers import POSSaleController

INJECTABLES = [
    POSConfirmSaleCommandHandler,
    POSCancelSaleCommandHandler,
    POSSaleController,
]
