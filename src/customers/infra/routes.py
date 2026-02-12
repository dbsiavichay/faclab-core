from fastapi import APIRouter, Query
from wireup import Injected

from src.customers.infra.controllers import (
    CustomerContactController,
    CustomerController,
)
from src.customers.infra.validators import (
    CustomerContactInput,
    CustomerContactResponse,
    CustomerContactsResponse,
    CustomerInput,
    CustomerResponse,
    CustomersResponse,
)


class CustomerRouter:
    """CustomerRouter using wireup Injected[] pattern for scoped controller."""

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
            "", response_model=CustomersResponse, summary="Get all customers"
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
            response_model=CustomerContactsResponse,
            summary="Get customer contacts",
        )(self.get_customer_contacts)

    def create(
        self,
        controller: Injected[CustomerController],
        new_customer: CustomerInput,
    ):
        """Creates a new customer."""
        return controller.create(new_customer)

    def update(
        self,
        controller: Injected[CustomerController],
        id: int,
        customer: CustomerInput,
    ):
        """Updates a customer."""
        return controller.update(id, customer)

    def delete(
        self,
        controller: Injected[CustomerController],
        id: int,
    ):
        """Deletes a customer."""
        return controller.delete(id)

    def get_all(
        self, controller: Injected[CustomerController]
    ):
        """Retrieves all customers."""
        customers = controller.get_all()
        return CustomersResponse(data=customers)

    def get_by_id(
        self, controller: Injected[CustomerController], id: int
    ):
        """Retrieves a specific customer by its ID."""
        return controller.get_by_id(id)

    def get_by_tax_id(
        self,
        controller: Injected[CustomerController],
        tax_id: str = Query(..., description="Tax ID to search for"),
    ):
        """Retrieves a customer by tax ID."""
        return controller.get_by_tax_id(tax_id)

    def activate(
        self, controller: Injected[CustomerController], id: int
    ):
        """Activates a customer."""
        return controller.activate(id)

    def deactivate(
        self, controller: Injected[CustomerController], id: int
    ):
        """Deactivates a customer."""
        return controller.deactivate(id)

    def create_contact(
        self,
        controller: Injected[CustomerContactController],
        customer_id: int,
        new_contact: CustomerContactInput,
    ):
        """Creates a new contact for a customer."""
        return controller.create(customer_id, new_contact)

    def get_customer_contacts(
        self,
        controller: Injected[CustomerContactController],
        customer_id: int,
    ):
        """Retrieves all contacts for a customer."""
        contacts = controller.get_by_customer_id(customer_id)
        return CustomerContactsResponse(data=contacts)


class CustomerContactRouter:
    """CustomerContactRouter using wireup Injected[] pattern for scoped controller."""

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
        controller: Injected[CustomerContactController],
        id: int,
        contact: CustomerContactInput,
    ):
        """Updates a customer contact."""
        return controller.update(id, contact)

    def delete(
        self,
        controller: Injected[CustomerContactController],
        id: int,
    ):
        """Deletes a customer contact."""
        return controller.delete(id)

    def get_by_id(
        self,
        controller: Injected[CustomerContactController],
        id: int,
    ):
        """Retrieves a specific customer contact by its ID."""
        return controller.get_by_id(id)
