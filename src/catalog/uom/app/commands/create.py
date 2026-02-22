from dataclasses import dataclass

from wireup import injectable

from src.catalog.uom.domain.entities import UnitOfMeasure
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository


@dataclass
class CreateUnitOfMeasureCommand(Command):
    name: str
    symbol: str
    description: str | None = None
    is_active: bool = True


@injectable(lifetime="scoped")
class CreateUnitOfMeasureCommandHandler(
    CommandHandler[CreateUnitOfMeasureCommand, dict]
):
    def __init__(self, repo: Repository[UnitOfMeasure]):
        self.repo = repo

    def _handle(self, command: CreateUnitOfMeasureCommand) -> dict:
        uom = UnitOfMeasure(
            name=command.name,
            symbol=command.symbol,
            description=command.description,
            is_active=command.is_active,
        )
        uom = self.repo.create(uom)
        return uom.dict()
