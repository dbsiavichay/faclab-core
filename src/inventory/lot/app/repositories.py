from src.inventory.lot.domain.entities import Lot, MovementLotItem
from src.shared.app.repositories import Repository


class LotRepository(Repository[Lot]):
    pass


class MovementLotItemRepository(Repository[MovementLotItem]):
    pass
