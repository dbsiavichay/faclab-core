from sqlalchemy.orm import Session
from wireup import injectable

from src.inventory.lot.domain.entities import Lot, MovementLotItem
from src.inventory.lot.infra.mappers import LotMapper, MovementLotItemMapper
from src.inventory.lot.infra.models import LotModel, MovementLotItemModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=Repository[Lot])
class LotRepository(SqlAlchemyRepository[Lot]):
    __model__ = LotModel

    def __init__(self, session: Session, mapper: LotMapper):
        super().__init__(session, mapper)

    def find_by_product_and_lot_number(
        self, product_id: int, lot_number: str
    ) -> Lot | None:
        return self.first(product_id=product_id, lot_number=lot_number)


@injectable(lifetime="scoped", as_type=Repository[MovementLotItem])
class MovementLotItemRepository(SqlAlchemyRepository[MovementLotItem]):
    __model__ = MovementLotItemModel

    def __init__(self, session: Session, mapper: MovementLotItemMapper):
        super().__init__(session, mapper)
