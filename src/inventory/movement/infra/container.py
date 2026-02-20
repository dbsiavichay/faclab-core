from src.inventory.movement.app.commands.movement import CreateMovementCommandHandler
from src.inventory.movement.app.queries.movement import (
    GetAllMovementsQueryHandler,
    GetMovementByIdQueryHandler,
)
from src.inventory.movement.infra.controllers import MovementController
from src.inventory.movement.infra.mappers import MovementMapper
from src.inventory.movement.infra.repositories import MovementRepository

INJECTABLES = [
    MovementMapper,
    MovementRepository,
    CreateMovementCommandHandler,
    GetAllMovementsQueryHandler,
    GetMovementByIdQueryHandler,
    MovementController,
]
