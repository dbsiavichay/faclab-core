
from src.customers.domain.entities import Customer, CustomerContact
from src.customers.infra.models import CustomerContactModel, CustomerModel
from src.shared.infra.repositories import BaseRepository


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
