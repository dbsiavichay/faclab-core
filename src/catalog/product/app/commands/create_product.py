from dataclasses import dataclass

from wireup import injectable

from src.catalog.product.domain.entities import Product
from src.catalog.product.domain.events import ProductCreated
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.events import EventPublisher
from src.shared.app.repositories import Repository


@dataclass
class CreateProductCommand(Command):
    sku: str
    name: str
    description: str | None = None
    category_id: int | None = None


@injectable(lifetime="scoped")
class CreateProductCommandHandler(CommandHandler[CreateProductCommand, dict]):
    def __init__(self, repo: Repository[Product], event_publisher: EventPublisher):
        self.repo = repo
        self.event_publisher = event_publisher

    def _handle(self, command: CreateProductCommand) -> dict:
        product = Product(
            sku=command.sku,
            name=command.name,
            description=command.description,
            category_id=command.category_id,
        )
        product = self.repo.create(product)

        self.event_publisher.publish(
            ProductCreated(
                aggregate_id=product.id,
                product_id=product.id,
                sku=product.sku,
                name=product.name,
                category_id=product.category_id,
            )
        )

        return product.dict()
