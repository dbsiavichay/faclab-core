from dataclasses import dataclass

from wireup import injectable

from src.inventory.warehouse.domain.entities import Warehouse
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class DeleteWarehouseCommand(Command):
    warehouse_id: int


@injectable(lifetime="scoped")
class DeleteWarehouseCommandHandler(CommandHandler[DeleteWarehouseCommand, None]):
    def __init__(self, repo: Repository[Warehouse]):
        self.repo = repo

    def _handle(self, command: DeleteWarehouseCommand) -> None:
        warehouse = self.repo.get_by_id(command.warehouse_id)
        if warehouse is None:
            raise NotFoundError(f"Warehouse {command.warehouse_id} not found")
        self.repo.delete(command.warehouse_id)
