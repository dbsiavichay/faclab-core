from dataclasses import dataclass

from wireup import injectable

from src.inventory.location.app.repositories import LocationRepository
from src.shared.app.commands import Command, CommandHandler
from src.shared.domain.exceptions import NotFoundError


@dataclass
class DeleteLocationCommand(Command):
    location_id: int


@injectable(lifetime="scoped")
class DeleteLocationCommandHandler(CommandHandler[DeleteLocationCommand, None]):
    def __init__(self, repo: LocationRepository):
        self.repo = repo

    def _handle(self, command: DeleteLocationCommand) -> None:
        location = self.repo.get_by_id(command.location_id)
        if location is None:
            raise NotFoundError(f"Location {command.location_id} not found")
        self.repo.delete(command.location_id)
