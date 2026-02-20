from fastapi import APIRouter, Query
from wireup import Injected

from src.customers.app.commands.customer import (
    ActivateCustomerCommand,
    ActivateCustomerCommandHandler,
    CreateCustomerCommand,
    CreateCustomerCommandHandler,
    DeactivateCustomerCommand,
    DeactivateCustomerCommandHandler,
    DeleteCustomerCommand,
    DeleteCustomerCommandHandler,
    UpdateCustomerCommand,
    UpdateCustomerCommandHandler,
)
from src.customers.app.commands.customer_contact import (
    CreateCustomerContactCommand,
    CreateCustomerContactCommandHandler,
    DeleteCustomerContactCommand,
    DeleteCustomerContactCommandHandler,
    UpdateCustomerContactCommand,
    UpdateCustomerContactCommandHandler,
)
from src.customers.app.queries.customer import (
    GetAllCustomersQuery,
    GetAllCustomersQueryHandler,
    GetCustomerByIdQuery,
    GetCustomerByIdQueryHandler,
    GetCustomerByTaxIdQuery,
    GetCustomerByTaxIdQueryHandler,
)
from src.customers.app.queries.customer_contact import (
    GetContactsByCustomerIdQuery,
    GetContactsByCustomerIdQueryHandler,
    GetCustomerContactByIdQuery,
    GetCustomerContactByIdQueryHandler,
)
from src.customers.infra.validators import (
    CustomerContactRequest,
    CustomerContactResponse,
    CustomerRequest,
    CustomerResponse,
)


class CustomerRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Sets up all the routes for the router."""
        self.router.post(
            "", response_model=CustomerResponse, summary="Create customer"
        )(self.create)
        self.router.put(
            "/{id}", response_model=CustomerResponse, summary="Update customer"
        )(self.update)
        self.router.delete("/{id}", summary="Delete customer")(self.delete)
        self.router.get(
            "", response_model=list[CustomerResponse], summary="Get all customers"
        )(self.get_all)
        self.router.get(
            "/{id}", response_model=CustomerResponse, summary="Get customer by ID"
        )(self.get_by_id)
        self.router.get(
            "/search/by-tax-id",
            response_model=CustomerResponse,
            summary="Get customer by tax ID",
        )(self.get_by_tax_id)
        self.router.post(
            "/{id}/activate",
            response_model=CustomerResponse,
            summary="Activate customer",
        )(self.activate)
        self.router.post(
            "/{id}/deactivate",
            response_model=CustomerResponse,
            summary="Deactivate customer",
        )(self.deactivate)
        self.router.post(
            "/{customer_id}/contacts",
            response_model=CustomerContactResponse,
            summary="Create customer contact",
        )(self.create_contact)
        self.router.get(
            "/{customer_id}/contacts",
            response_model=list[CustomerContactResponse],
            summary="Get customer contacts",
        )(self.get_customer_contacts)

    def create(
        self,
        handler: Injected[CreateCustomerCommandHandler],
        new_customer: CustomerRequest,
    ) -> CustomerResponse:
        """Creates a new customer."""
        result = handler.handle(
            CreateCustomerCommand(**new_customer.model_dump(exclude_none=True))
        )
        return CustomerResponse.model_validate(result)

    def update(
        self,
        handler: Injected[UpdateCustomerCommandHandler],
        id: int,
        customer: CustomerRequest,
    ) -> CustomerResponse:
        """Updates a customer."""
        result = handler.handle(
            UpdateCustomerCommand(id=id, **customer.model_dump(exclude_none=True))
        )
        return CustomerResponse.model_validate(result)

    def delete(
        self,
        handler: Injected[DeleteCustomerCommandHandler],
        id: int,
    ) -> None:
        """Deletes a customer."""
        handler.handle(DeleteCustomerCommand(id=id))

    def get_all(
        self, handler: Injected[GetAllCustomersQueryHandler]
    ) -> list[CustomerResponse]:
        """Retrieves all customers."""
        result = handler.handle(GetAllCustomersQuery())
        return [CustomerResponse.model_validate(c) for c in result]

    def get_by_id(
        self, handler: Injected[GetCustomerByIdQueryHandler], id: int
    ) -> CustomerResponse:
        """Retrieves a specific customer by its ID."""
        result = handler.handle(GetCustomerByIdQuery(id=id))
        return CustomerResponse.model_validate(result)

    def get_by_tax_id(
        self,
        handler: Injected[GetCustomerByTaxIdQueryHandler],
        tax_id: str = Query(..., description="Tax ID to search for"),
    ) -> CustomerResponse:
        """Retrieves a customer by tax ID."""
        result = handler.handle(GetCustomerByTaxIdQuery(tax_id=tax_id))
        return CustomerResponse.model_validate(result)

    def activate(
        self, handler: Injected[ActivateCustomerCommandHandler], id: int
    ) -> CustomerResponse:
        """Activates a customer."""
        result = handler.handle(ActivateCustomerCommand(id=id))
        return CustomerResponse.model_validate(result)

    def deactivate(
        self, handler: Injected[DeactivateCustomerCommandHandler], id: int
    ) -> CustomerResponse:
        """Deactivates a customer."""
        result = handler.handle(DeactivateCustomerCommand(id=id))
        return CustomerResponse.model_validate(result)

    def create_contact(
        self,
        handler: Injected[CreateCustomerContactCommandHandler],
        customer_id: int,
        new_contact: CustomerContactRequest,
    ) -> CustomerContactResponse:
        """Creates a new contact for a customer."""
        result = handler.handle(
            CreateCustomerContactCommand(
                customer_id=customer_id, **new_contact.model_dump(exclude_none=True)
            )
        )
        return CustomerContactResponse.model_validate(result)

    def get_customer_contacts(
        self,
        handler: Injected[GetContactsByCustomerIdQueryHandler],
        customer_id: int,
    ) -> list[CustomerContactResponse]:
        """Retrieves all contacts for a customer."""
        result = handler.handle(GetContactsByCustomerIdQuery(customer_id=customer_id))
        return [CustomerContactResponse.model_validate(c) for c in result]


class CustomerContactRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Sets up all the routes for the router."""
        self.router.put(
            "/{id}",
            response_model=CustomerContactResponse,
            summary="Update customer contact",
        )(self.update)
        self.router.delete("/{id}", summary="Delete customer contact")(self.delete)
        self.router.get(
            "/{id}",
            response_model=CustomerContactResponse,
            summary="Get customer contact by ID",
        )(self.get_by_id)

    def update(
        self,
        handler: Injected[UpdateCustomerContactCommandHandler],
        id: int,
        contact: CustomerContactRequest,
    ) -> CustomerContactResponse:
        """Updates a customer contact."""
        result = handler.handle(
            UpdateCustomerContactCommand(id=id, **contact.model_dump(exclude_none=True))
        )
        return CustomerContactResponse.model_validate(result)

    def delete(
        self,
        handler: Injected[DeleteCustomerContactCommandHandler],
        id: int,
    ) -> None:
        """Deletes a customer contact."""
        handler.handle(DeleteCustomerContactCommand(id=id))

    def get_by_id(
        self,
        handler: Injected[GetCustomerContactByIdQueryHandler],
        id: int,
    ) -> CustomerContactResponse:
        """Retrieves a specific customer contact by its ID."""
        result = handler.handle(GetCustomerContactByIdQuery(id=id))
        return CustomerContactResponse.model_validate(result)
