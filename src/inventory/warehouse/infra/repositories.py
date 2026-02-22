from sqlalchemy.orm import Session
from wireup import injectable

from src.inventory.warehouse.domain.entities import Warehouse
from src.inventory.warehouse.infra.mappers import WarehouseMapper
from src.inventory.warehouse.infra.models import WarehouseModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=Repository[Warehouse])
class WarehouseRepository(SqlAlchemyRepository[Warehouse]):
    __model__ = WarehouseModel

    def __init__(self, session: Session, mapper: WarehouseMapper):
        super().__init__(session, mapper)
