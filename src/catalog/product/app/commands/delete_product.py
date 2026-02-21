from dataclasses import dataclass

from wireup import injectable

from src.catalog.product.domain.entities import Product
from src.catalog.product.domain.events import ProductDeleted
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.events import EventPublisher
from src.shared.app.repositories import Repository


@dataclass
class DeleteProductCommand(Command):
    product_id: int


@injectable(lifetime="scoped")
class DeleteProductCommandHandler(CommandHandler[DeleteProductCommand, None]):
    def __init__(self, repo: Repository[Product], event_publisher: EventPublisher):
        self.repo = repo
        self.event_publisher = event_publisher

    def _handle(self, command: DeleteProductCommand) -> None:
        self.repo.delete(command.product_id)

        self.event_publisher.publish(
            ProductDeleted(
                aggregate_id=command.product_id,
                product_id=command.product_id,
            )
        )
