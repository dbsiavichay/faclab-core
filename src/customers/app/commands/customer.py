from dataclasses import dataclass, replace
from decimal import Decimal

from wireup import injectable

from src.customers.domain.entities import Customer, TaxType
from src.customers.domain.events import (
    CustomerActivated,
    CustomerCreated,
    CustomerDeactivated,
    CustomerUpdated,
)
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError
from src.shared.domain.value_objects import Email, TaxId
from src.shared.infra.events.event_bus import EventBus


@dataclass
class CreateCustomerCommand(Command):
    name: str = ""
    tax_id: str = ""
    tax_type: int = 1
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    credit_limit: Decimal | None = None
    payment_terms: int | None = None
    is_active: bool = True


@injectable(lifetime="scoped")
class CreateCustomerCommandHandler(CommandHandler[CreateCustomerCommand, dict]):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def _handle(self, command: CreateCustomerCommand) -> dict:
        if command.email:
            Email(command.email)
        TaxId(command.tax_id)

        customer = Customer(
            name=command.name,
            tax_id=command.tax_id,
            tax_type=TaxType(command.tax_type),
            email=command.email,
            phone=command.phone,
            address=command.address,
            city=command.city,
            state=command.state,
            country=command.country,
            credit_limit=command.credit_limit,
            payment_terms=command.payment_terms,
            is_active=command.is_active,
        )
        customer = self.repo.create(customer)

        EventBus.publish(
            CustomerCreated(
                aggregate_id=customer.id,
                customer_id=customer.id,
                name=customer.name,
                tax_id=customer.tax_id,
            )
        )
        return customer.dict()


@dataclass
class UpdateCustomerCommand(Command):
    id: int = 0
    name: str = ""
    tax_id: str = ""
    tax_type: int = 1
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    credit_limit: Decimal | None = None
    payment_terms: int | None = None
    is_active: bool = True


@injectable(lifetime="scoped")
class UpdateCustomerCommandHandler(CommandHandler[UpdateCustomerCommand, dict]):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def _handle(self, command: UpdateCustomerCommand) -> dict:
        if command.email:
            Email(command.email)
        TaxId(command.tax_id)

        customer = Customer(
            id=command.id,
            name=command.name,
            tax_id=command.tax_id,
            tax_type=TaxType(command.tax_type),
            email=command.email,
            phone=command.phone,
            address=command.address,
            city=command.city,
            state=command.state,
            country=command.country,
            credit_limit=command.credit_limit,
            payment_terms=command.payment_terms,
            is_active=command.is_active,
        )
        customer = self.repo.update(customer)

        EventBus.publish(
            CustomerUpdated(
                aggregate_id=customer.id,
                customer_id=customer.id,
                name=customer.name,
            )
        )
        return customer.dict()


@dataclass
class DeleteCustomerCommand(Command):
    id: int = 0


@injectable(lifetime="scoped")
class DeleteCustomerCommandHandler(CommandHandler[DeleteCustomerCommand, None]):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def _handle(self, command: DeleteCustomerCommand) -> None:
        self.repo.delete(command.id)


@dataclass
class ActivateCustomerCommand(Command):
    id: int = 0


@injectable(lifetime="scoped")
class ActivateCustomerCommandHandler(CommandHandler[ActivateCustomerCommand, dict]):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def _handle(self, command: ActivateCustomerCommand) -> dict:
        customer = self.repo.get_by_id(command.id)
        if customer is None:
            raise NotFoundError(f"Customer with id {command.id} not found")

        updated_customer = replace(customer, is_active=True)
        updated_customer = self.repo.update(updated_customer)

        EventBus.publish(
            CustomerActivated(
                aggregate_id=updated_customer.id,
                customer_id=updated_customer.id,
            )
        )
        return updated_customer.dict()


@dataclass
class DeactivateCustomerCommand(Command):
    id: int = 0


@injectable(lifetime="scoped")
class DeactivateCustomerCommandHandler(CommandHandler[DeactivateCustomerCommand, dict]):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def _handle(self, command: DeactivateCustomerCommand) -> dict:
        customer = self.repo.get_by_id(command.id)
        if customer is None:
            raise NotFoundError(f"Customer with id {command.id} not found")

        updated_customer = replace(customer, is_active=False)
        updated_customer = self.repo.update(updated_customer)

        EventBus.publish(
            CustomerDeactivated(
                aggregate_id=updated_customer.id,
                customer_id=updated_customer.id,
            )
        )
        return updated_customer.dict()
