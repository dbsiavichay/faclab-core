from dataclasses import dataclass

from wireup import injectable

from src.inventory.movement.domain.constants import MovementType
from src.inventory.movement.domain.entities import Movement
from src.inventory.stock.domain.entities import Stock
from src.sales.domain.entities import Sale, SaleItem
from src.sales.domain.events import SaleConfirmed
from src.sales.domain.exceptions import InsufficientStockError, SaleHasNoItemsError
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.events import EventPublisher
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class POSConfirmSaleCommand(Command):
    sale_id: int


@injectable(lifetime="scoped")
class POSConfirmSaleCommandHandler(CommandHandler[POSConfirmSaleCommand, dict]):
    def __init__(
        self,
        sale_repo: Repository[Sale],
        sale_item_repo: Repository[SaleItem],
        movement_repo: Repository[Movement],
        stock_repo: Repository[Stock],
        event_publisher: EventPublisher,
    ):
        self.sale_repo = sale_repo
        self.sale_item_repo = sale_item_repo
        self.movement_repo = movement_repo
        self.stock_repo = stock_repo
        self.event_publisher = event_publisher

    def _handle(self, command: POSConfirmSaleCommand) -> dict:
        sale = self.sale_repo.get_by_id(command.sale_id)
        if not sale:
            raise NotFoundError(f"Sale with id {command.sale_id} not found")

        items = self.sale_item_repo.filter_by(sale_id=command.sale_id)
        if not items:
            raise SaleHasNoItemsError(command.sale_id)

        for item in items:
            stock = self.stock_repo.first(product_id=item.product_id)
            available = stock.quantity if stock else 0
            if available < item.quantity:
                raise InsufficientStockError(item.product_id, item.quantity, available)

        sale.confirm()
        self.sale_repo.update(sale)

        for item in items:
            movement = Movement(
                product_id=item.product_id,
                quantity=-abs(item.quantity),
                type=MovementType.OUT,
                reason=f"Sale #{command.sale_id} confirmed",
            )
            self.movement_repo.create(movement)

            stock = self.stock_repo.first(product_id=item.product_id)
            stock.update_quantity(-abs(item.quantity))
            self.stock_repo.update(stock)

        items_data = [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
            }
            for item in items
        ]

        self.event_publisher.publish(
            SaleConfirmed(
                aggregate_id=sale.id,
                sale_id=sale.id,
                customer_id=sale.customer_id,
                items=items_data,
                total=float(sale.total),
                source="pos",
            )
        )

        return sale.dict()
