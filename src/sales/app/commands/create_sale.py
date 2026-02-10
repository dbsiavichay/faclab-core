from dataclasses import dataclass
from typing import Optional

from src.sales.domain.entities import Sale
from src.sales.domain.events import SaleCreated
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.infra.events.event_bus import EventBus


@dataclass
class CreateSaleCommand(Command):
    """Comando para crear una nueva venta"""

    customer_id: int
    notes: Optional[str] = None
    created_by: Optional[str] = None


class CreateSaleCommandHandler(CommandHandler[CreateSaleCommand, dict]):
    """Handler para crear una nueva venta en estado DRAFT"""

    def __init__(self, repo: Repository[Sale]):
        self.repo = repo

    def handle(self, command: CreateSaleCommand) -> dict:
        """Crea una nueva venta en estado DRAFT"""
        sale = Sale(
            customer_id=command.customer_id,
            notes=command.notes,
            created_by=command.created_by,
        )

        sale = self.repo.create(sale)

        # Publicar evento
        EventBus.publish(
            SaleCreated(
                aggregate_id=sale.id,
                sale_id=sale.id,
                customer_id=sale.customer_id,
                total=float(sale.total),
            )
        )

        return sale.dict()
