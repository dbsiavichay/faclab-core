from sqlalchemy.orm import Session
from wireup import injectable

from src.inventory.serial.domain.entities import SerialNumber
from src.inventory.serial.infra.mappers import SerialNumberMapper
from src.inventory.serial.infra.models import SerialNumberModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=Repository[SerialNumber])
class SerialNumberRepository(SqlAlchemyRepository[SerialNumber]):
    __model__ = SerialNumberModel

    def __init__(self, session: Session, mapper: SerialNumberMapper):
        super().__init__(session, mapper)

    def find_by_serial(self, serial_number: str) -> SerialNumber | None:
        return self.first(serial_number=serial_number)
