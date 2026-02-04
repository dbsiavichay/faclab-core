from typing import List

from src.customers.app.use_cases import (
    ActivateCustomerUseCase,
    CreateCustomerContactUseCase,
    CreateCustomerUseCase,
    DeactivateCustomerUseCase,
    DeleteCustomerContactUseCase,
    DeleteCustomerUseCase,
    GetAllCustomersUseCase,
    GetContactsByCustomerIdUseCase,
    GetCustomerByIdUseCase,
    GetCustomerByTaxIdUseCase,
    GetCustomerContactByIdUseCase,
    UpdateCustomerContactUseCase,
    UpdateCustomerUseCase,
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
        create_customer: CreateCustomerUseCase,
        update_customer: UpdateCustomerUseCase,
        delete_customer: DeleteCustomerUseCase,
        get_all_customers: GetAllCustomersUseCase,
        get_customer_by_id: GetCustomerByIdUseCase,
        get_customer_by_tax_id: GetCustomerByTaxIdUseCase,
        activate_customer: ActivateCustomerUseCase,
        deactivate_customer: DeactivateCustomerUseCase,
    ):
        self.create_customer = create_customer
        self.update_customer = update_customer
        self.delete_customer = delete_customer
        self.get_all_customers = get_all_customers
        self.get_customer_by_id = get_customer_by_id
        self.get_customer_by_tax_id = get_customer_by_tax_id
        self.activate_customer = activate_customer
        self.deactivate_customer = deactivate_customer

    def create(self, new_customer: CustomerInput) -> CustomerResponse:
        customer = self.create_customer.execute(
            new_customer.model_dump(exclude_none=True)
        )
        return CustomerResponse.model_validate(customer)

    def update(self, id: int, customer: CustomerInput) -> CustomerResponse:
        customer = self.update_customer.execute(
            id, customer.model_dump(exclude_none=True)
        )
        return CustomerResponse.model_validate(customer)

    def delete(self, id: int) -> None:
        self.delete_customer.execute(id)

    def get_all(self) -> List[CustomerResponse]:
        customers = self.get_all_customers.execute()
        return [CustomerResponse.model_validate(customer) for customer in customers]

    def get_by_id(self, id: int) -> CustomerResponse:
        customer = self.get_customer_by_id.execute(id)
        if customer is None:
            raise NotFoundException("Customer not found")
        return CustomerResponse.model_validate(customer)

    def get_by_tax_id(self, tax_id: str) -> CustomerResponse:
        customer = self.get_customer_by_tax_id.execute(tax_id)
        if customer is None:
            raise NotFoundException(f"Customer with tax_id {tax_id} not found")
        return CustomerResponse.model_validate(customer)

    def activate(self, id: int) -> CustomerResponse:
        customer = self.activate_customer.execute(id)
        return CustomerResponse.model_validate(customer)

    def deactivate(self, id: int) -> CustomerResponse:
        customer = self.deactivate_customer.execute(id)
        return CustomerResponse.model_validate(customer)


class CustomerContactController:
    def __init__(
        self,
        create_contact: CreateCustomerContactUseCase,
        update_contact: UpdateCustomerContactUseCase,
        delete_contact: DeleteCustomerContactUseCase,
        get_contact_by_id: GetCustomerContactByIdUseCase,
        get_contacts_by_customer_id: GetContactsByCustomerIdUseCase,
    ):
        self.create_contact = create_contact
        self.update_contact = update_contact
        self.delete_contact = delete_contact
        self.get_contact_by_id = get_contact_by_id
        self.get_contacts_by_customer_id = get_contacts_by_customer_id

    def create(
        self, customer_id: int, new_contact: CustomerContactInput
    ) -> CustomerContactResponse:
        contact = self.create_contact.execute(
            customer_id, new_contact.model_dump(exclude_none=True)
        )
        return CustomerContactResponse.model_validate(contact)

    def update(self, id: int, contact: CustomerContactInput) -> CustomerContactResponse:
        contact = self.update_contact.execute(id, contact.model_dump(exclude_none=True))
        return CustomerContactResponse.model_validate(contact)

    def delete(self, id: int) -> None:
        self.delete_contact.execute(id)

    def get_by_id(self, id: int) -> CustomerContactResponse:
        contact = self.get_contact_by_id.execute(id)
        if contact is None:
            raise NotFoundException("Customer contact not found")
        return CustomerContactResponse.model_validate(contact)

    def get_by_customer_id(self, customer_id: int) -> List[CustomerContactResponse]:
        contacts = self.get_contacts_by_customer_id.execute(customer_id)
        return [CustomerContactResponse.model_validate(contact) for contact in contacts]
