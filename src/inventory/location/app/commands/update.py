from dataclasses import dataclass

from wireup import injectable

from src.inventory.location.domain.entities import Location, LocationType
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class UpdateLocationCommand(Command):
    location_id: int
    warehouse_id: int
    name: str
    code: str
    type: str = LocationType.STORAGE
    is_active: bool = True
    capacity: int | None = None


@injectable(lifetime="scoped")
class UpdateLocationCommandHandler(CommandHandler[UpdateLocationCommand, dict]):
    def __init__(self, repo: Repository[Location]):
        self.repo = repo

    def _handle(self, command: UpdateLocationCommand) -> dict:
        location = self.repo.get_by_id(command.location_id)
        if location is None:
            raise NotFoundError(f"Location {command.location_id} not found")
        location = Location(
            id=command.location_id,
            warehouse_id=command.warehouse_id,
            name=command.name,
            code=command.code,
            type=LocationType(command.type),
            is_active=command.is_active,
            capacity=command.capacity,
        )
        location = self.repo.update(location)
        return location.dict()
