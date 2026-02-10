from dataclasses import dataclass
from decimal import Decimal

from src.sales.domain.entities import Sale, SaleItem
from src.sales.domain.events import SaleItemRemoved
from src.sales.domain.exceptions import InvalidSaleStatusException
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.infra.events.event_bus import EventBus
from src.shared.infra.exceptions import NotFoundException


@dataclass
class RemoveSaleItemCommand(Command):
    """Comando para eliminar un item de una venta"""

    sale_id: int
    sale_item_id: int


class RemoveSaleItemCommandHandler(CommandHandler[RemoveSaleItemCommand, dict]):
    """Handler para eliminar un item de una venta y recalcular totales"""

    def __init__(
        self,
        sale_repo: Repository[Sale],
        sale_item_repo: Repository[SaleItem],
    ):
        self.sale_repo = sale_repo
        self.sale_item_repo = sale_item_repo

    def handle(self, command: RemoveSaleItemCommand) -> dict:
        """Elimina un item de la venta y recalcula los totales"""
        # Obtener la venta
        sale = self.sale_repo.get_by_id(command.sale_id)
        if not sale:
            raise NotFoundException(f"Sale with id {command.sale_id} not found")

        # Validar que la venta esté en DRAFT
        if sale.status.value != "DRAFT":
            raise InvalidSaleStatusException(sale.status.value, "remove items from")

        # Obtener el item
        sale_item = self.sale_item_repo.get_by_id(command.sale_item_id)
        if not sale_item:
            raise NotFoundException(
                f"Sale item with id {command.sale_item_id} not found"
            )

        # Verificar que el item pertenece a la venta
        if sale_item.sale_id != command.sale_id:
            raise ValueError(
                f"Sale item {command.sale_item_id} does not belong to "
                f"sale {command.sale_id}"
            )

        # Guardar info del item para el evento
        item_dict = sale_item.dict()

        # Eliminar el item
        self.sale_item_repo.delete(sale_item)

        # Recalcular totales de la venta
        items = self.sale_item_repo.filter_by(sale_id=command.sale_id)
        subtotal = sum(item.subtotal for item in items)

        # Aplicar descuento general si existe
        discount_amount = subtotal * (sale.discount / Decimal("100"))
        subtotal_after_discount = subtotal - discount_amount

        # Calcular impuestos
        tax_amount = subtotal_after_discount * (sale.tax / Decimal("100"))
        total = subtotal_after_discount + tax_amount

        # Actualizar la venta
        sale.subtotal = subtotal
        sale.total = total
        self.sale_repo.update(sale)

        # Publicar evento
        EventBus.publish(
            SaleItemRemoved(
                aggregate_id=sale.id,
                sale_id=sale.id,
                sale_item_id=sale_item.id,
                product_id=sale_item.product_id,
                quantity=sale_item.quantity,
            )
        )

        return {"success": True, "removed_item": item_dict}
