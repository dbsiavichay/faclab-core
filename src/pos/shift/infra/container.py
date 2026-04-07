from src.pos.shift.app.commands.close_shift import CloseShiftCommandHandler
from src.pos.shift.app.commands.open_shift import OpenShiftCommandHandler
from src.pos.shift.app.queries.get_shifts import (
    GetActiveShiftQueryHandler,
    GetAllShiftsQueryHandler,
    GetShiftByIdQueryHandler,
)
from src.pos.shift.infra.mappers import ShiftMapper
from src.pos.shift.infra.repositories import SqlAlchemyShiftRepository

INJECTABLES = [
    ShiftMapper,
    SqlAlchemyShiftRepository,
    OpenShiftCommandHandler,
    CloseShiftCommandHandler,
    GetActiveShiftQueryHandler,
    GetShiftByIdQueryHandler,
    GetAllShiftsQueryHandler,
]
