from src.inventory.adjustment.app.commands.adjustment import (
    AddAdjustmentItemCommandHandler,
    CancelAdjustmentCommandHandler,
    ConfirmAdjustmentCommandHandler,
    CreateAdjustmentCommandHandler,
    DeleteAdjustmentCommandHandler,
    RemoveAdjustmentItemCommandHandler,
    UpdateAdjustmentCommandHandler,
    UpdateAdjustmentItemCommandHandler,
)
from src.inventory.adjustment.app.queries.adjustment import (
    GetAdjustmentByIdQueryHandler,
    GetAdjustmentItemsQueryHandler,
    GetAllAdjustmentsQueryHandler,
)
from src.inventory.adjustment.infra.mappers import (
    AdjustmentItemMapper,
    InventoryAdjustmentMapper,
)
from src.inventory.adjustment.infra.repositories import (
    AdjustmentItemRepository,
    InventoryAdjustmentRepository,
)

ADJUSTMENT_INJECTABLES = [
    InventoryAdjustmentMapper,
    AdjustmentItemMapper,
    InventoryAdjustmentRepository,
    AdjustmentItemRepository,
    CreateAdjustmentCommandHandler,
    UpdateAdjustmentCommandHandler,
    DeleteAdjustmentCommandHandler,
    ConfirmAdjustmentCommandHandler,
    CancelAdjustmentCommandHandler,
    AddAdjustmentItemCommandHandler,
    UpdateAdjustmentItemCommandHandler,
    RemoveAdjustmentItemCommandHandler,
    GetAllAdjustmentsQueryHandler,
    GetAdjustmentByIdQueryHandler,
    GetAdjustmentItemsQueryHandler,
]
