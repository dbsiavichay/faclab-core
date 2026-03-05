from src.inventory.lot.app.commands.lot import (
    CreateLotCommandHandler,
    UpdateLotCommandHandler,
)
from src.inventory.lot.app.queries.lot import (
    GetAllLotsQueryHandler,
    GetLotByIdQueryHandler,
)
from src.inventory.lot.infra.mappers import LotMapper, MovementLotItemMapper
from src.inventory.lot.infra.repositories import (
    LotRepository,
    MovementLotItemRepository,
)

LOT_INJECTABLES = [
    LotMapper,
    MovementLotItemMapper,
    LotRepository,
    MovementLotItemRepository,
    CreateLotCommandHandler,
    UpdateLotCommandHandler,
    GetAllLotsQueryHandler,
    GetLotByIdQueryHandler,
]
