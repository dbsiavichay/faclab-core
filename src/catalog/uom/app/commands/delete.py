from dataclasses import dataclass

from wireup import injectable

from src.catalog.uom.app.repositories import UnitOfMeasureRepository
from src.shared.app.commands import Command, CommandHandler
from src.shared.domain.exceptions import NotFoundError


@dataclass
class DeleteUnitOfMeasureCommand(Command):
    uom_id: int


@injectable(lifetime="scoped")
class DeleteUnitOfMeasureCommandHandler(
    CommandHandler[DeleteUnitOfMeasureCommand, None]
):
    def __init__(self, repo: UnitOfMeasureRepository):
        self.repo = repo

    def _handle(self, command: DeleteUnitOfMeasureCommand) -> None:
        existing = self.repo.get_by_id(command.uom_id)
        if existing is None:
            raise NotFoundError(f"Unit of measure with id {command.uom_id} not found")
        self.repo.delete(command.uom_id)
