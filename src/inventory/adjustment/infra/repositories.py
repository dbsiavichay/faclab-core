from sqlalchemy.orm import Session
from wireup import injectable

from src.inventory.adjustment.app.repositories import (
    AdjustmentItemRepository,
    InventoryAdjustmentRepository,
)
from src.inventory.adjustment.domain.entities import AdjustmentItem, InventoryAdjustment
from src.inventory.adjustment.infra.mappers import (
    AdjustmentItemMapper,
    InventoryAdjustmentMapper,
)
from src.inventory.adjustment.infra.models import (
    AdjustmentItemModel,
    InventoryAdjustmentModel,
)
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=InventoryAdjustmentRepository)
class SqlAlchemyInventoryAdjustmentRepository(
    SqlAlchemyRepository[InventoryAdjustment], InventoryAdjustmentRepository
):
    __model__ = InventoryAdjustmentModel

    def __init__(self, session: Session, mapper: InventoryAdjustmentMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=AdjustmentItemRepository)
class SqlAlchemyAdjustmentItemRepository(
    SqlAlchemyRepository[AdjustmentItem], AdjustmentItemRepository
):
    __model__ = AdjustmentItemModel

    def __init__(self, session: Session, mapper: AdjustmentItemMapper):
        super().__init__(session, mapper)
