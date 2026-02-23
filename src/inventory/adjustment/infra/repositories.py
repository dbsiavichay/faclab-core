from sqlalchemy.orm import Session
from wireup import injectable

from src.inventory.adjustment.domain.entities import AdjustmentItem, InventoryAdjustment
from src.inventory.adjustment.infra.mappers import (
    AdjustmentItemMapper,
    InventoryAdjustmentMapper,
)
from src.inventory.adjustment.infra.models import (
    AdjustmentItemModel,
    InventoryAdjustmentModel,
)
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=Repository[InventoryAdjustment])
class InventoryAdjustmentRepository(SqlAlchemyRepository[InventoryAdjustment]):
    __model__ = InventoryAdjustmentModel

    def __init__(self, session: Session, mapper: InventoryAdjustmentMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=Repository[AdjustmentItem])
class AdjustmentItemRepository(SqlAlchemyRepository[AdjustmentItem]):
    __model__ = AdjustmentItemModel

    def __init__(self, session: Session, mapper: AdjustmentItemMapper):
        super().__init__(session, mapper)
