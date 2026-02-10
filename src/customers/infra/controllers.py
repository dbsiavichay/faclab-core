from typing import List

from src.customers.app.commands import (
    ActivateCustomerCommand,
    ActivateCustomerCommandHandler,
    CreateCustomerCommand,
    CreateCustomerCommandHandler,
    CreateCustomerContactCommand,
    CreateCustomerContactCommandHandler,
    DeactivateCustomerCommand,
    DeactivateCustomerCommandHandler,
    DeleteCustomerCommand,
    DeleteCustomerCommandHandler,
    DeleteCustomerContactCommand,
    DeleteCustomerContactCommandHandler,
    UpdateCustomerCommand,
    UpdateCustomerCommandHandler,
    UpdateCustomerContactCommand,
    UpdateCustomerContactCommandHandler,
)
from src.customers.app.queries import (
    GetAllCustomersQuery,
    GetAllCustomersQueryHandler,
    GetContactsByCustomerIdQuery,
    GetContactsByCustomerIdQueryHandler,
    GetCustomerByIdQuery,
    GetCustomerByIdQueryHandler,
    GetCustomerByTaxIdQuery,
    GetCustomerByTaxIdQueryHandler,
    GetCustomerContactByIdQuery,
    GetCustomerContactByIdQueryHandler,
)
from src.customers.infra.validators import (
    CustomerContactInput,
    CustomerContactResponse,
    CustomerInput,
    CustomerResponse,
)
from src.shared.infra.exceptions import NotFoundException


class CustomerController:
    def __init__(
        self,
        create_handler: CreateCustomerCommandHandler,
        update_handler: UpdateCustomerCommandHandler,
        delete_handler: DeleteCustomerCommandHandler,
        activate_handler: ActivateCustomerCommandHandler,
        deactivate_handler: DeactivateCustomerCommandHandler,
        get_all_handler: GetAllCustomersQueryHandler,
        get_by_id_handler: GetCustomerByIdQueryHandler,
        get_by_tax_id_handler: GetCustomerByTaxIdQueryHandler,
    ):
        self.create_handler = create_handler
        self.update_handler = update_handler
        self.delete_handler = delete_handler
        self.activate_handler = activate_handler
        self.deactivate_handler = deactivate_handler
        self.get_all_handler = get_all_handler
        self.get_by_id_handler = get_by_id_handler
        self.get_by_tax_id_handler = get_by_tax_id_handler

    def create(self, new_customer: CustomerInput) -> CustomerResponse:
        command = CreateCustomerCommand(**new_customer.model_dump(exclude_none=True))
        result = self.create_handler.handle(command)
        return CustomerResponse.model_validate(result)

    def update(self, id: int, customer: CustomerInput) -> CustomerResponse:
        command = UpdateCustomerCommand(id=id, **customer.model_dump(exclude_none=True))
        result = self.update_handler.handle(command)
        return CustomerResponse.model_validate(result)

    def delete(self, id: int) -> None:
        self.delete_handler.handle(DeleteCustomerCommand(id=id))

    def get_all(self) -> List[CustomerResponse]:
        customers = self.get_all_handler.handle(GetAllCustomersQuery())
        return [CustomerResponse.model_validate(customer) for customer in customers]

    def get_by_id(self, id: int) -> CustomerResponse:
        customer = self.get_by_id_handler.handle(GetCustomerByIdQuery(id=id))
        if customer is None:
            raise NotFoundException("Customer not found")
        return CustomerResponse.model_validate(customer)

    def get_by_tax_id(self, tax_id: str) -> CustomerResponse:
        customer = self.get_by_tax_id_handler.handle(
            GetCustomerByTaxIdQuery(tax_id=tax_id)
        )
        if customer is None:
            raise NotFoundException(f"Customer with tax_id {tax_id} not found")
        return CustomerResponse.model_validate(customer)

    def activate(self, id: int) -> CustomerResponse:
        result = self.activate_handler.handle(ActivateCustomerCommand(id=id))
        return CustomerResponse.model_validate(result)

    def deactivate(self, id: int) -> CustomerResponse:
        result = self.deactivate_handler.handle(DeactivateCustomerCommand(id=id))
        return CustomerResponse.model_validate(result)


class CustomerContactController:
    def __init__(
        self,
        create_handler: CreateCustomerContactCommandHandler,
        update_handler: UpdateCustomerContactCommandHandler,
        delete_handler: DeleteCustomerContactCommandHandler,
        get_by_id_handler: GetCustomerContactByIdQueryHandler,
        get_by_customer_id_handler: GetContactsByCustomerIdQueryHandler,
    ):
        self.create_handler = create_handler
        self.update_handler = update_handler
        self.delete_handler = delete_handler
        self.get_by_id_handler = get_by_id_handler
        self.get_by_customer_id_handler = get_by_customer_id_handler

    def create(
        self, customer_id: int, new_contact: CustomerContactInput
    ) -> CustomerContactResponse:
        command = CreateCustomerContactCommand(
            customer_id=customer_id, **new_contact.model_dump(exclude_none=True)
        )
        result = self.create_handler.handle(command)
        return CustomerContactResponse.model_validate(result)

    def update(self, id: int, contact: CustomerContactInput) -> CustomerContactResponse:
        command = UpdateCustomerContactCommand(
            id=id, **contact.model_dump(exclude_none=True)
        )
        result = self.update_handler.handle(command)
        return CustomerContactResponse.model_validate(result)

    def delete(self, id: int) -> None:
        self.delete_handler.handle(DeleteCustomerContactCommand(id=id))

    def get_by_id(self, id: int) -> CustomerContactResponse:
        contact = self.get_by_id_handler.handle(GetCustomerContactByIdQuery(id=id))
        if contact is None:
            raise NotFoundException("Customer contact not found")
        return CustomerContactResponse.model_validate(contact)

    def get_by_customer_id(self, customer_id: int) -> List[CustomerContactResponse]:
        contacts = self.get_by_customer_id_handler.handle(
            GetContactsByCustomerIdQuery(customer_id=customer_id)
        )
        return [CustomerContactResponse.model_validate(contact) for contact in contacts]
