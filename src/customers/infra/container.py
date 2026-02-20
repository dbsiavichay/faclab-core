from src.customers.app.commands.customer import (
    ActivateCustomerCommandHandler,
    CreateCustomerCommandHandler,
    DeactivateCustomerCommandHandler,
    DeleteCustomerCommandHandler,
    UpdateCustomerCommandHandler,
)
from src.customers.app.commands.customer_contact import (
    CreateCustomerContactCommandHandler,
    DeleteCustomerContactCommandHandler,
    UpdateCustomerContactCommandHandler,
)
from src.customers.app.queries.customer import (
    GetAllCustomersQueryHandler,
    GetCustomerByIdQueryHandler,
    GetCustomerByTaxIdQueryHandler,
)
from src.customers.app.queries.customer_contact import (
    GetContactsByCustomerIdQueryHandler,
    GetCustomerContactByIdQueryHandler,
)
from src.customers.infra.mappers import CustomerContactMapper, CustomerMapper
from src.customers.infra.repositories import (
    CustomerContactRepository,
    CustomerRepository,
)

INJECTABLES = [
    CustomerMapper,
    CustomerContactMapper,
    CustomerRepository,
    CustomerContactRepository,
    CreateCustomerCommandHandler,
    UpdateCustomerCommandHandler,
    DeleteCustomerCommandHandler,
    ActivateCustomerCommandHandler,
    DeactivateCustomerCommandHandler,
    GetAllCustomersQueryHandler,
    GetCustomerByIdQueryHandler,
    GetCustomerByTaxIdQueryHandler,
    CreateCustomerContactCommandHandler,
    UpdateCustomerContactCommandHandler,
    DeleteCustomerContactCommandHandler,
    GetCustomerContactByIdQueryHandler,
    GetContactsByCustomerIdQueryHandler,
]
