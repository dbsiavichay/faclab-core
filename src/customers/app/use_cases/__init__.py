from src.customers.app.use_cases.customer import (
    ActivateCustomerUseCase,
    CreateCustomerUseCase,
    DeactivateCustomerUseCase,
    DeleteCustomerUseCase,
    GetAllCustomersUseCase,
    GetCustomerByIdUseCase,
    GetCustomerByTaxIdUseCase,
    UpdateCustomerUseCase,
)
from src.customers.app.use_cases.customer_contact import (
    CreateCustomerContactUseCase,
    DeleteCustomerContactUseCase,
    GetContactsByCustomerIdUseCase,
    GetCustomerContactByIdUseCase,
    UpdateCustomerContactUseCase,
)

__all__ = [
    # Customer use cases
    "CreateCustomerUseCase",
    "UpdateCustomerUseCase",
    "DeleteCustomerUseCase",
    "GetCustomerByIdUseCase",
    "GetAllCustomersUseCase",
    "GetCustomerByTaxIdUseCase",
    "ActivateCustomerUseCase",
    "DeactivateCustomerUseCase",
    # Customer contact use cases
    "CreateCustomerContactUseCase",
    "UpdateCustomerContactUseCase",
    "DeleteCustomerContactUseCase",
    "GetCustomerContactByIdUseCase",
    "GetContactsByCustomerIdUseCase",
]
