from dataclasses import dataclass

from wireup import injectable

from src.catalog.product.domain.entities import Product
from src.catalog.product.domain.events import ProductDeleted
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.infra.events.event_bus import EventBus


@dataclass
class DeleteProductCommand(Command):
    product_id: int


@injectable(lifetime="scoped")
class DeleteProductCommandHandler(CommandHandler[DeleteProductCommand, None]):
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def _handle(self, command: DeleteProductCommand) -> None:
        self.repo.delete(command.product_id)

        EventBus.publish(
            ProductDeleted(
                aggregate_id=command.product_id,
                product_id=command.product_id,
            )
        )
