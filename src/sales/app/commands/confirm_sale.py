from dataclasses import dataclass

from wireup import injectable

from src.sales.domain.entities import Sale, SaleItem
from src.sales.domain.events import SaleConfirmed
from src.sales.domain.exceptions import SaleHasNoItemsError
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.infra.events.event_bus import EventBus
from src.shared.infra.exceptions import NotFoundError


@dataclass
class ConfirmSaleCommand(Command):
    """Comando para confirmar una venta"""

    sale_id: int


@injectable(lifetime="scoped")
class ConfirmSaleCommandHandler(CommandHandler[ConfirmSaleCommand, dict]):
    """
    Handler para confirmar una venta.
    Emite el evento SaleConfirmed que será escuchado por Inventory
    para crear movimientos OUT.
    """

    def __init__(
        self,
        sale_repo: Repository[Sale],
        sale_item_repo: Repository[SaleItem],
    ):
        self.sale_repo = sale_repo
        self.sale_item_repo = sale_item_repo

    def handle(self, command: ConfirmSaleCommand) -> dict:
        """Confirma la venta si pasa todas las validaciones"""
        # Obtener la venta
        sale = self.sale_repo.get_by_id(command.sale_id)
        if not sale:
            raise NotFoundError(f"Sale with id {command.sale_id} not found")

        # Obtener los items
        items = self.sale_item_repo.filter_by(sale_id=command.sale_id)

        # Validar que tenga items
        if not items:
            raise SaleHasNoItemsError(command.sale_id)

        # Confirmar la venta (esto valida el estado internamente)
        sale.confirm()
        sale = self.sale_repo.update(sale)

        # Preparar items para el evento
        items_data = [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
            }
            for item in items
        ]

        # Publicar evento SaleConfirmed
        # Este evento será escuchado por Inventory para crear movimientos OUT
        EventBus.publish(
            SaleConfirmed(
                aggregate_id=sale.id,
                sale_id=sale.id,
                customer_id=sale.customer_id,
                items=items_data,
                total=float(sale.total),
            )
        )

        return sale.dict()
