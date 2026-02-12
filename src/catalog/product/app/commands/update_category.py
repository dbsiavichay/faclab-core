from dataclasses import dataclass

from wireup import injectable

from src.catalog.product.domain.entities import Category
from src.catalog.product.domain.events import CategoryUpdated
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.infra.events.event_bus import EventBus


@dataclass
class UpdateCategoryCommand(Command):
    category_id: int
    name: str
    description: str | None = None


@injectable(lifetime="scoped")
class UpdateCategoryCommandHandler(CommandHandler[UpdateCategoryCommand, dict]):
    def __init__(self, repo: Repository[Category]):
        self.repo = repo

    def handle(self, command: UpdateCategoryCommand) -> dict:
        # Get existing category to track changes
        existing = self.repo.get_by_id(command.category_id)

        category = Category(
            id=command.category_id,
            name=command.name,
            description=command.description,
        )
        category = self.repo.update(category)

        # Track what changed
        changes = {}
        if existing:
            if existing.name != category.name:
                changes['name'] = {'old': existing.name, 'new': category.name}
            if existing.description != category.description:
                changes['description'] = {'old': existing.description, 'new': category.description}

        EventBus.publish(
            CategoryUpdated(
                aggregate_id=category.id,
                category_id=category.id,
                changes=changes,
            )
        )

        return category.dict()
