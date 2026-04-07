from src.customers.domain.entities import Customer, CustomerContact
from src.shared.app.repositories import Repository


class CustomerRepository(Repository[Customer]):
    pass


class CustomerContactRepository(Repository[CustomerContact]):
    pass
