from dataclasses import dataclass

from wireup import injectable

from src.inventory.warehouse.domain.entities import Warehouse
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository


@dataclass
class CreateWarehouseCommand(Command):
    name: str
    code: str
    address: str | None = None
    city: str | None = None
    country: str | None = None
    is_active: bool = True
    is_default: bool = False
    manager: str | None = None
    phone: str | None = None
    email: str | None = None


@injectable(lifetime="scoped")
class CreateWarehouseCommandHandler(CommandHandler[CreateWarehouseCommand, dict]):
    def __init__(self, repo: Repository[Warehouse]):
        self.repo = repo

    def _handle(self, command: CreateWarehouseCommand) -> dict:
        warehouse = Warehouse(
            name=command.name,
            code=command.code,
            address=command.address,
            city=command.city,
            country=command.country,
            is_active=command.is_active,
            is_default=command.is_default,
            manager=command.manager,
            phone=command.phone,
            email=command.email,
        )
        warehouse = self.repo.create(warehouse)
        return warehouse.dict()
