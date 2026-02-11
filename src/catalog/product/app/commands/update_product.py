from dataclasses import dataclass
from typing import Optional

from src.catalog.product.domain.entities import Product
from src.catalog.product.domain.events import ProductUpdated
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.infra.events.event_bus import EventBus


@dataclass
class UpdateProductCommand(Command):
    product_id: int
    sku: str
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None


class UpdateProductCommandHandler(CommandHandler[UpdateProductCommand, dict]):
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def handle(self, command: UpdateProductCommand) -> dict:
        # Get existing product to track changes
        existing = self.repo.get_by_id(command.product_id)

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
        if existing:
            if existing.sku != product.sku:
                changes['sku'] = {'old': existing.sku, 'new': product.sku}
            if existing.name != product.name:
                changes['name'] = {'old': existing.name, 'new': product.name}
            if existing.description != product.description:
                changes['description'] = {'old': existing.description, 'new': product.description}
            if existing.category_id != product.category_id:
                changes['category_id'] = {'old': existing.category_id, 'new': product.category_id}

        EventBus.publish(
            ProductUpdated(
                aggregate_id=product.id,
                product_id=product.id,
                changes=changes,
            )
        )

        return product.dict()
