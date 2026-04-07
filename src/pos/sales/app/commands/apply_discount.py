from dataclasses import dataclass
from decimal import Decimal

from wireup import injectable

from src.sales.app.repositories import SaleItemRepository, SaleRepository
from src.sales.domain.exceptions import InvalidSaleStatusError
from src.sales.domain.services import recalculate_sale_totals
from src.shared.app.commands import Command, CommandHandler
from src.shared.domain.exceptions import NotFoundError, ValidationError


@dataclass
class ApplySaleDiscountCommand(Command):
    """Comando para aplicar descuento a nivel de venta"""

    sale_id: int
    discount_type: str
    discount_value: Decimal


@injectable(lifetime="scoped")
class ApplySaleDiscountCommandHandler(CommandHandler[ApplySaleDiscountCommand, dict]):
    """Handler para aplicar descuento a una venta y recalcular totales"""

    def __init__(
        self,
        sale_repo: SaleRepository,
        sale_item_repo: SaleItemRepository,
    ):
        self.sale_repo = sale_repo
        self.sale_item_repo = sale_item_repo

    def _handle(self, command: ApplySaleDiscountCommand) -> dict:
        sale = self.sale_repo.get_by_id(command.sale_id)
        if not sale:
            raise NotFoundError(f"Sale with id {command.sale_id} not found")

        if sale.status.value != "DRAFT":
            raise InvalidSaleStatusError(sale.status.value, "apply discount to")

        if command.discount_type not in ("PERCENTAGE", "AMOUNT"):
            raise ValidationError(
                f"Invalid discount_type: {command.discount_type}. "
                "Must be PERCENTAGE or AMOUNT"
            )

        if command.discount_value < Decimal("0"):
            raise ValidationError("discount_value must be non-negative")

        if command.discount_type == "PERCENTAGE" and command.discount_value > Decimal(
            "100"
        ):
            raise ValidationError("Percentage discount cannot exceed 100")

        sale.discount_type = command.discount_type
        sale.discount_value = command.discount_value

        items = self.sale_item_repo.filter_by(sale_id=command.sale_id)
        recalculate_sale_totals(sale, items)
        self.sale_repo.update(sale)

        return sale.dict()
