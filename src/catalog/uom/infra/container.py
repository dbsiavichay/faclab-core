from src.catalog.uom.app.commands.create import CreateUnitOfMeasureCommandHandler
from src.catalog.uom.app.commands.delete import DeleteUnitOfMeasureCommandHandler
from src.catalog.uom.app.commands.update import UpdateUnitOfMeasureCommandHandler
from src.catalog.uom.app.queries.get_uom import (
    GetAllUnitsOfMeasureQueryHandler,
    GetUnitOfMeasureByIdQueryHandler,
)
from src.catalog.uom.infra.mappers import UnitOfMeasureMapper
from src.catalog.uom.infra.repositories import UnitOfMeasureRepository

INJECTABLES = [
    UnitOfMeasureMapper,
    UnitOfMeasureRepository,
    CreateUnitOfMeasureCommandHandler,
    UpdateUnitOfMeasureCommandHandler,
    DeleteUnitOfMeasureCommandHandler,
    GetAllUnitsOfMeasureQueryHandler,
    GetUnitOfMeasureByIdQueryHandler,
]
