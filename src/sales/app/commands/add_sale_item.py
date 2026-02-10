from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from src.sales.domain.entities import Sale, SaleItem
from src.sales.domain.events import SaleItemAdded
from src.sales.domain.exceptions import InvalidSaleStatusException
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.infra.events.event_bus import EventBus
from src.shared.infra.exceptions import NotFoundException


@dataclass
class AddSaleItemCommand(Command):
    """Comando para agregar un item a una venta"""

    sale_id: int
    product_id: int
    quantity: int
    unit_price: float
    discount: Optional[float] = 0.0


class AddSaleItemCommandHandler(CommandHandler[AddSaleItemCommand, dict]):
    """Handler para agregar un item a una venta y recalcular totales"""

    def __init__(
        self,
        sale_repo: Repository[Sale],
        sale_item_repo: Repository[SaleItem],
    ):
        self.sale_repo = sale_repo
        self.sale_item_repo = sale_item_repo

    def handle(self, command: AddSaleItemCommand) -> dict:
        """Agrega un item a la venta y recalcula los totales"""
        # Obtener la venta
        sale = self.sale_repo.get_by_id(command.sale_id)
        if not sale:
            raise NotFoundException(f"Sale with id {command.sale_id} not found")

        # Validar que la venta esté en DRAFT
        if sale.status.value != "DRAFT":
            raise InvalidSaleStatusException(sale.status.value, "add items to")

        # Crear el item
        sale_item = SaleItem(
            sale_id=command.sale_id,
            product_id=command.product_id,
            quantity=command.quantity,
            unit_price=Decimal(str(command.unit_price)),
            discount=Decimal(str(command.discount)),
        )

        sale_item = self.sale_item_repo.create(sale_item)

        # Recalcular totales de la venta
        items = self.sale_item_repo.filter_by(sale_id=command.sale_id)
        subtotal = sum(item.subtotal for item in items)

        # Aplicar descuento general si existe
        discount_amount = subtotal * (sale.discount / Decimal("100"))
        subtotal_after_discount = subtotal - discount_amount

        # Calcular impuestos (asumiendo 12% IVA en Ecuador)
        tax_amount = subtotal_after_discount * (sale.tax / Decimal("100"))
        total = subtotal_after_discount + tax_amount

        # Actualizar la venta
        sale.subtotal = subtotal
        sale.total = total
        self.sale_repo.update(sale)

        # Publicar evento
        EventBus.publish(
            SaleItemAdded(
                aggregate_id=sale.id,
                sale_id=sale.id,
                sale_item_id=sale_item.id,
                product_id=sale_item.product_id,
                quantity=sale_item.quantity,
                unit_price=float(sale_item.unit_price),
            )
        )

        return sale_item.dict()
