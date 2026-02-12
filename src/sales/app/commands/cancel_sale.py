from dataclasses import dataclass

from wireup import injectable

from src.sales.domain.entities import Sale, SaleItem, SaleStatus
from src.sales.domain.events import SaleCancelled
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.infra.events.event_bus import EventBus
from src.shared.infra.exceptions import NotFoundException


@dataclass
class CancelSaleCommand(Command):
    """Comando para cancelar una venta"""

    sale_id: int
    reason: str | None = None


@injectable(lifetime="scoped")
class CancelSaleCommandHandler(CommandHandler[CancelSaleCommand, dict]):
    """
    Handler para cancelar una venta.
    Si la venta estaba confirmada, emite SaleCancelled para revertir movimientos.
    """

    def __init__(
        self,
        sale_repo: Repository[Sale],
        sale_item_repo: Repository[SaleItem],
    ):
        self.sale_repo = sale_repo
        self.sale_item_repo = sale_item_repo

    def handle(self, command: CancelSaleCommand) -> dict:
        """Cancela la venta y emite evento si es necesario"""
        # Obtener la venta
        sale = self.sale_repo.get_by_id(command.sale_id)
        if not sale:
            raise NotFoundException(f"Sale with id {command.sale_id} not found")

        # Verificar si estaba confirmada (para revertir inventario)
        was_confirmed = sale.status == SaleStatus.CONFIRMED

        # Cancelar la venta (esto valida el estado internamente)
        sale.cancel()
        sale = self.sale_repo.update(sale)

        # Si estaba confirmada, obtener items para revertir movimientos
        items_data = []
        if was_confirmed:
            items = self.sale_item_repo.filter_by(sale_id=command.sale_id)
            items_data = [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                }
                for item in items
            ]

        # Publicar evento SaleCancelled
        # Si was_confirmed=True, Inventory creará movimientos IN de reversión
        EventBus.publish(
            SaleCancelled(
                aggregate_id=sale.id,
                sale_id=sale.id,
                customer_id=sale.customer_id,
                items=items_data,
                reason=command.reason or "",
                was_confirmed=was_confirmed,
            )
        )

        return sale.dict()
