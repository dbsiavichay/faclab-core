from src.pos.sales.app.commands import (
    POSCancelSaleCommandHandler,
    POSConfirmSaleCommandHandler,
)

INJECTABLES = [
    POSConfirmSaleCommandHandler,
    POSCancelSaleCommandHandler,
]
