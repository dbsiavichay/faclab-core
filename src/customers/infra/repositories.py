from sqlalchemy.orm import Session
from wireup import injectable

from src.customers.domain.entities import Customer, CustomerContact
from src.customers.infra.mappers import CustomerContactMapper, CustomerMapper
from src.customers.infra.models import CustomerContactModel, CustomerModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import BaseRepository


@injectable(lifetime="scoped")
class CustomerRepositoryImpl(BaseRepository[Customer]):
    """Implementation of the CustomerRepository interface using SQLAlchemy
    This class provides methods to interact with the customer data in the database
    through SQLAlchemy ORM.
    """

    __model__ = CustomerModel

    def get_by_tax_id(self, tax_id: str) -> Customer | None:
        """Get customer by tax ID"""
        model = self.session.query(self.__model__).filter_by(tax_id=tax_id).first()
        return self.mapper.to_entity(model)


@injectable(lifetime="scoped", as_type=Repository[Customer])
def create_customer_repository(
    session: Session, mapper: CustomerMapper
) -> Repository[Customer]:
    """Factory function for creating CustomerRepository with generic type binding.

    Args:
        session: Scoped database session (injected by wireup)
        mapper: CustomerMapper instance (injected by wireup)

    Returns:
        Repository[Customer]: Customer repository implementation
    """
    return CustomerRepositoryImpl(session, mapper)


@injectable(lifetime="scoped")
class CustomerContactRepositoryImpl(BaseRepository[CustomerContact]):
    """Implementation of the CustomerContactRepository interface using SQLAlchemy
    This class provides methods to interact
    with the customer contact data in the database
    through SQLAlchemy ORM.
    """

    __model__ = CustomerContactModel

    def get_by_customer_id(self, customer_id: int) -> list[CustomerContact]:
        """Get all contacts for a specific customer"""
        models = (
            self.session.query(self.__model__).filter_by(customer_id=customer_id).all()
        )
        return [self.mapper.to_entity(model) for model in models]


@injectable(lifetime="scoped", as_type=Repository[CustomerContact])
def create_customer_contact_repository(
    session: Session, mapper: CustomerContactMapper
) -> Repository[CustomerContact]:
    """Factory function for creating CustomerContactRepository with generic type binding.

    Args:
        session: Scoped database session (injected by wireup)
        mapper: CustomerContactMapper instance (injected by wireup)

    Returns:
        Repository[CustomerContact]: Customer contact repository implementation
    """
    return CustomerContactRepositoryImpl(session, mapper)
