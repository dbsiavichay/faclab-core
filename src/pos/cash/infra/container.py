from src.pos.cash.app.commands.register_cash_movement import (
    RegisterCashMovementCommandHandler,
)
from src.pos.cash.app.queries.get_cash_movements import GetCashMovementsQueryHandler
from src.pos.cash.app.queries.get_cash_summary import GetCashSummaryQueryHandler
from src.pos.cash.infra.mappers import CashMovementMapper
from src.pos.cash.infra.repositories import CashMovementRepository

POS_CASH_INJECTABLES = [
    CashMovementMapper,
    CashMovementRepository,
    RegisterCashMovementCommandHandler,
    GetCashMovementsQueryHandler,
    GetCashSummaryQueryHandler,
]
