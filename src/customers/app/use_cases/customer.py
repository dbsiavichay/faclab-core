from typing import Optional

from src.customers.app.types import CustomerInput, CustomerOutput
from src.customers.domain.entities import Customer
from src.shared.app.repositories import Repository


class CreateCustomerUseCase:
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def execute(self, customer_create: CustomerInput) -> CustomerOutput:
        customer = Customer(**customer_create)
        customer = self.repo.create(customer)
        return customer.dict()


class UpdateCustomerUseCase:
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def execute(self, id: int, customer_update: CustomerInput) -> CustomerOutput:
        customer = Customer(id=id, **customer_update)
        customer = self.repo.update(customer)
        return customer.dict()


class DeleteCustomerUseCase:
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def execute(self, id: int) -> None:
        return self.repo.delete(id)


class GetCustomerByIdUseCase:
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def execute(self, id: int) -> Optional[CustomerOutput]:
        customer = self.repo.get_by_id(id)
        if customer is None:
            return None
        return customer.dict()


class GetAllCustomersUseCase:
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def execute(self) -> list[CustomerOutput]:
        customers = self.repo.get_all()
        return [customer.dict() for customer in customers]


class GetCustomerByTaxIdUseCase:
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def execute(self, tax_id: str) -> Optional[CustomerOutput]:
        # Use custom method from repository
        from src.customers.infra.repositories import CustomerRepositoryImpl

        if isinstance(self.repo, CustomerRepositoryImpl):
            customer = self.repo.get_by_tax_id(tax_id)
            if customer is None:
                return None
            return customer.dict()
        return None


class ActivateCustomerUseCase:
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def execute(self, id: int) -> CustomerOutput:
        customer = self.repo.get_by_id(id)
        if customer is None:
            raise ValueError(f"Customer with id {id} not found")

        # Create updated customer with is_active=True
        from dataclasses import replace

        updated_customer = replace(customer, is_active=True)
        updated_customer = self.repo.update(updated_customer)
        return updated_customer.dict()


class DeactivateCustomerUseCase:
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def execute(self, id: int) -> CustomerOutput:
        customer = self.repo.get_by_id(id)
        if customer is None:
            raise ValueError(f"Customer with id {id} not found")

        # Create updated customer with is_active=False
        from dataclasses import replace

        updated_customer = replace(customer, is_active=False)
        updated_customer = self.repo.update(updated_customer)
        return updated_customer.dict()
