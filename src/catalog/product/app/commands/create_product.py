from dataclasses import dataclass

from wireup import injectable

from src.catalog.product.domain.entities import Product
from src.catalog.product.domain.events import ProductCreated
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.infra.events.event_bus import EventBus


@dataclass
class CreateProductCommand(Command):
    sku: str
    name: str
    description: str | None = None
    category_id: int | None = None


@injectable(lifetime="scoped")
class CreateProductCommandHandler(CommandHandler[CreateProductCommand, dict]):
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def handle(self, command: CreateProductCommand) -> dict:
        product = Product(
            sku=command.sku,
            name=command.name,
            description=command.description,
            category_id=command.category_id,
        )
        product = self.repo.create(product)

        EventBus.publish(
            ProductCreated(
                aggregate_id=product.id,
                product_id=product.id,
                sku=product.sku,
                name=product.name,
                category_id=product.category_id,
            )
        )

        return product.dict()
