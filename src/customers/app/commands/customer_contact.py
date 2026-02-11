from dataclasses import dataclass

from src.customers.app.types import CustomerContactOutput
from src.customers.domain.entities import CustomerContact
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository


@dataclass
class CreateCustomerContactCommand(Command):
    customer_id: int = 0
    name: str = ""
    role: str | None = None
    email: str | None = None
    phone: str | None = None


class CreateCustomerContactCommandHandler(
    CommandHandler[CreateCustomerContactCommand, CustomerContactOutput]
):
    def __init__(self, repo: Repository[CustomerContact]):
        self.repo = repo

    def handle(self, command: CreateCustomerContactCommand) -> CustomerContactOutput:
        contact = CustomerContact(
            customer_id=command.customer_id,
            name=command.name,
            role=command.role,
            email=command.email,
            phone=command.phone,
        )
        contact = self.repo.create(contact)
        return contact.dict()


@dataclass
class UpdateCustomerContactCommand(Command):
    id: int = 0
    customer_id: int = 0
    name: str = ""
    role: str | None = None
    email: str | None = None
    phone: str | None = None


class UpdateCustomerContactCommandHandler(
    CommandHandler[UpdateCustomerContactCommand, CustomerContactOutput]
):
    def __init__(self, repo: Repository[CustomerContact]):
        self.repo = repo

    def handle(self, command: UpdateCustomerContactCommand) -> CustomerContactOutput:
        contact = CustomerContact(
            id=command.id,
            customer_id=command.customer_id,
            name=command.name,
            role=command.role,
            email=command.email,
            phone=command.phone,
        )
        contact = self.repo.update(contact)
        return contact.dict()


@dataclass
class DeleteCustomerContactCommand(Command):
    id: int = 0


class DeleteCustomerContactCommandHandler(
    CommandHandler[DeleteCustomerContactCommand, None]
):
    def __init__(self, repo: Repository[CustomerContact]):
        self.repo = repo

    def handle(self, command: DeleteCustomerContactCommand) -> None:
        self.repo.delete(command.id)
