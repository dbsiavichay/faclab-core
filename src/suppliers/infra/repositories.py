from sqlalchemy.orm import Session
from wireup import injectable

from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository
from src.suppliers.domain.entities import Supplier, SupplierContact, SupplierProduct
from src.suppliers.infra.mappers import (
    SupplierContactMapper,
    SupplierMapper,
    SupplierProductMapper,
)
from src.suppliers.infra.models import (
    SupplierContactModel,
    SupplierModel,
    SupplierProductModel,
)


@injectable(lifetime="scoped", as_type=Repository[Supplier])
class SupplierRepository(SqlAlchemyRepository[Supplier]):
    __model__ = SupplierModel

    def __init__(self, session: Session, mapper: SupplierMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=Repository[SupplierContact])
class SupplierContactRepository(SqlAlchemyRepository[SupplierContact]):
    __model__ = SupplierContactModel

    def __init__(self, session: Session, mapper: SupplierContactMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=Repository[SupplierProduct])
class SupplierProductRepository(SqlAlchemyRepository[SupplierProduct]):
    __model__ = SupplierProductModel

    def __init__(self, session: Session, mapper: SupplierProductMapper):
        super().__init__(session, mapper)
