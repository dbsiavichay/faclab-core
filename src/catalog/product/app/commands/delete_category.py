from dataclasses import dataclass

from wireup import injectable

from src.catalog.product.domain.entities import Category
from src.catalog.product.domain.events import CategoryDeleted
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.infra.events.event_bus import EventBus


@dataclass
class DeleteCategoryCommand(Command):
    category_id: int


@injectable(lifetime="scoped")
class DeleteCategoryCommandHandler(CommandHandler[DeleteCategoryCommand, None]):
    def __init__(self, repo: Repository[Category]):
        self.repo = repo

    def handle(self, command: DeleteCategoryCommand) -> None:
        self.repo.delete(command.category_id)

        EventBus.publish(
            CategoryDeleted(
                aggregate_id=command.category_id,
                category_id=command.category_id,
            )
        )
