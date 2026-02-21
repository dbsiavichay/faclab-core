from dataclasses import dataclass

from wireup import injectable

from src.catalog.product.domain.entities import Product
from src.catalog.product.domain.events import ProductUpdated
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.events import EventPublisher
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class UpdateProductCommand(Command):
    product_id: int
    sku: str
    name: str
    description: str | None = None
    category_id: int | None = None


@injectable(lifetime="scoped")
class UpdateProductCommandHandler(CommandHandler[UpdateProductCommand, dict]):
    def __init__(self, repo: Repository[Product], event_publisher: EventPublisher):
        self.repo = repo
        self.event_publisher = event_publisher

    def _handle(self, command: UpdateProductCommand) -> dict:
        # Get existing product to track changes
        existing = self.repo.get_by_id(command.product_id)
        if existing is None:
            raise NotFoundError(f"Product with id {command.product_id} not found")

        product = Product(
            id=command.product_id,
            sku=command.sku,
            name=command.name,
            description=command.description,
            category_id=command.category_id,
        )
        product = self.repo.update(product)

        # Track what changed
        changes = {}
        if existing.sku != product.sku:
            changes["sku"] = {"old": existing.sku, "new": product.sku}
        if existing.name != product.name:
            changes["name"] = {"old": existing.name, "new": product.name}
        if existing.description != product.description:
            changes["description"] = {
                "old": existing.description,
                "new": product.description,
            }
        if existing.category_id != product.category_id:
            changes["category_id"] = {
                "old": existing.category_id,
                "new": product.category_id,
            }

        self.event_publisher.publish(
            ProductUpdated(
                aggregate_id=product.id,
                product_id=product.id,
                changes=changes,
            )
        )

        return product.dict()
