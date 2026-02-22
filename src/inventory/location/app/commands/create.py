from dataclasses import dataclass

from wireup import injectable

from src.inventory.location.domain.entities import Location, LocationType
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository


@dataclass
class CreateLocationCommand(Command):
    warehouse_id: int
    name: str
    code: str
    type: str = LocationType.STORAGE
    is_active: bool = True
    capacity: int | None = None


@injectable(lifetime="scoped")
class CreateLocationCommandHandler(CommandHandler[CreateLocationCommand, dict]):
    def __init__(self, repo: Repository[Location]):
        self.repo = repo

    def _handle(self, command: CreateLocationCommand) -> dict:
        location = Location(
            warehouse_id=command.warehouse_id,
            name=command.name,
            code=command.code,
            type=LocationType(command.type),
            is_active=command.is_active,
            capacity=command.capacity,
        )
        location = self.repo.create(location)
        return location.dict()
