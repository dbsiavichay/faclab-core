from typing import Optional

from src.customers.app.types import CustomerContactInput, CustomerContactOutput
from src.customers.domain.entities import CustomerContact
from src.shared.app.repositories import Repository


class CreateCustomerContactUseCase:
    def __init__(self, repo: Repository[CustomerContact]):
        self.repo = repo

    def execute(
        self, customer_id: int, contact_create: CustomerContactInput
    ) -> CustomerContactOutput:
        # Ensure customer_id is set from the path parameter
        contact_data = dict(contact_create)
        contact_data["customer_id"] = customer_id
        contact = CustomerContact(**contact_data)
        contact = self.repo.create(contact)
        return contact.dict()


class UpdateCustomerContactUseCase:
    def __init__(self, repo: Repository[CustomerContact]):
        self.repo = repo

    def execute(
        self, id: int, contact_update: CustomerContactInput
    ) -> CustomerContactOutput:
        contact = CustomerContact(id=id, **contact_update)
        contact = self.repo.update(contact)
        return contact.dict()


class DeleteCustomerContactUseCase:
    def __init__(self, repo: Repository[CustomerContact]):
        self.repo = repo

    def execute(self, id: int) -> None:
        return self.repo.delete(id)


class GetCustomerContactByIdUseCase:
    def __init__(self, repo: Repository[CustomerContact]):
        self.repo = repo

    def execute(self, id: int) -> Optional[CustomerContactOutput]:
        contact = self.repo.get_by_id(id)
        if contact is None:
            return None
        return contact.dict()


class GetContactsByCustomerIdUseCase:
    def __init__(self, repo: Repository[CustomerContact]):
        self.repo = repo

    def execute(self, customer_id: int) -> list[CustomerContactOutput]:
        # Use custom method from repository
        from src.customers.infra.repositories import CustomerContactRepositoryImpl

        if isinstance(self.repo, CustomerContactRepositoryImpl):
            contacts = self.repo.get_by_customer_id(customer_id)
            return [contact.dict() for contact in contacts]
        return []
