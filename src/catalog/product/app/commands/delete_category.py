from dataclasses import dataclass

from wireup import injectable

from src.catalog.product.domain.entities import Category
from src.catalog.product.domain.events import CategoryDeleted
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.events import EventPublisher
from src.shared.app.repositories import Repository


@dataclass
class DeleteCategoryCommand(Command):
    category_id: int


@injectable(lifetime="scoped")
class DeleteCategoryCommandHandler(CommandHandler[DeleteCategoryCommand, None]):
    def __init__(self, repo: Repository[Category], event_publisher: EventPublisher):
        self.repo = repo
        self.event_publisher = event_publisher

    def _handle(self, command: DeleteCategoryCommand) -> None:
        self.repo.delete(command.category_id)

        self.event_publisher.publish(
            CategoryDeleted(
                aggregate_id=command.category_id,
                category_id=command.category_id,
            )
        )
