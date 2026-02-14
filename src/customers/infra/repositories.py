from sqlalchemy.orm import Session
from wireup import injectable

from src.customers.domain.entities import Customer, CustomerContact
from src.customers.infra.mappers import CustomerContactMapper, CustomerMapper
from src.customers.infra.models import CustomerContactModel, CustomerModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=Repository[Customer])
class CustomerRepository(SqlAlchemyRepository[Customer]):
    __model__ = CustomerModel

    def __init__(self, session: Session, mapper: CustomerMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=Repository[CustomerContact])
class CustomerContactRepository(SqlAlchemyRepository[CustomerContact]):
    __model__ = CustomerContactModel

    def __init__(self, session: Session, mapper: CustomerContactMapper):
        super().__init__(session, mapper)
