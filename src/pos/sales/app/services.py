"""POS transactional services for atomic sale operations"""

import structlog
from sqlalchemy.orm import Session
from wireup import injectable

from src.inventory.movement.domain.constants import MovementType
from src.inventory.movement.domain.entities import Movement
from src.inventory.movement.infra.mappers import MovementMapper
from src.inventory.movement.infra.models import MovementModel
from src.inventory.stock.domain.entities import Stock
from src.inventory.stock.infra.mappers import StockMapper
from src.inventory.stock.infra.models import StockModel
from src.sales.domain.entities import Sale, SaleItem, SaleStatus
from src.sales.domain.events import SaleCancelled, SaleConfirmed
from src.sales.domain.exceptions import InsufficientStockError, SaleHasNoItemsError
from src.sales.infra.mappers import SaleItemMapper, SaleMapper
from src.sales.infra.models import SaleItemModel, SaleModel
from src.shared.infra.events.event_bus import EventBus
from src.shared.infra.exceptions import NotFoundError
from src.shared.infra.repositories import SqlAlchemyRepository

logger = structlog.get_logger(__name__)


class _SaleRepo(SqlAlchemyRepository[Sale]):
    __model__ = SaleModel


class _SaleItemRepo(SqlAlchemyRepository[SaleItem]):
    __model__ = SaleItemModel


class _MovementRepo(SqlAlchemyRepository[Movement]):
    __model__ = MovementModel


class _StockRepo(SqlAlchemyRepository[Stock]):
    __model__ = StockModel


@injectable(lifetime="scoped")
class ConfirmSaleService:
    def __init__(
        self,
        session: Session,
        sale_mapper: SaleMapper,
        sale_item_mapper: SaleItemMapper,
        movement_mapper: MovementMapper,
        stock_mapper: StockMapper,
    ):
        self.session = session
        self.sale_repo = _SaleRepo(session, sale_mapper, auto_commit=False)
        self.sale_item_repo = _SaleItemRepo(
            session, sale_item_mapper, auto_commit=False
        )
        self.movement_repo = _MovementRepo(session, movement_mapper, auto_commit=False)
        self.stock_repo = _StockRepo(session, stock_mapper, auto_commit=False)

    def execute(self, sale_id: int) -> dict:
        sale = self.sale_repo.get_by_id(sale_id)
        if not sale:
            raise NotFoundError(f"Sale with id {sale_id} not found")

        items = self.sale_item_repo.filter_by(sale_id=sale_id)
        if not items:
            raise SaleHasNoItemsError(sale_id)

        # Validate stock for ALL items BEFORE mutating
        for item in items:
            stock = self.stock_repo.first(product_id=item.product_id)
            available = stock.quantity if stock else 0
            if available < item.quantity:
                raise InsufficientStockError(item.product_id, item.quantity, available)

        try:
            sale.confirm()
            self.sale_repo.update(sale)

            for item in items:
                movement = Movement(
                    product_id=item.product_id,
                    quantity=-abs(item.quantity),
                    type=MovementType.OUT,
                    reason=f"Sale #{sale_id} confirmed",
                )
                self.movement_repo.create(movement)

                stock = self.stock_repo.first(product_id=item.product_id)
                stock.update_quantity(-abs(item.quantity))
                self.stock_repo.update(stock)

            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        items_data = [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
            }
            for item in items
        ]

        EventBus.publish(
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


@injectable(lifetime="scoped")
class CancelSaleService:
    def __init__(
        self,
        session: Session,
        sale_mapper: SaleMapper,
        sale_item_mapper: SaleItemMapper,
        movement_mapper: MovementMapper,
        stock_mapper: StockMapper,
    ):
        self.session = session
        self.sale_repo = _SaleRepo(session, sale_mapper, auto_commit=False)
        self.sale_item_repo = _SaleItemRepo(
            session, sale_item_mapper, auto_commit=False
        )
        self.movement_repo = _MovementRepo(session, movement_mapper, auto_commit=False)
        self.stock_repo = _StockRepo(session, stock_mapper, auto_commit=False)

    def execute(self, sale_id: int, reason: str | None = None) -> dict:
        sale = self.sale_repo.get_by_id(sale_id)
        if not sale:
            raise NotFoundError(f"Sale with id {sale_id} not found")

        was_confirmed = sale.status == SaleStatus.CONFIRMED

        if was_confirmed:
            # Atomic: cancel + reverse inventory
            items = self.sale_item_repo.filter_by(sale_id=sale_id)

            try:
                sale.cancel()
                self.sale_repo.update(sale)

                for item in items:
                    movement = Movement(
                        product_id=item.product_id,
                        quantity=abs(item.quantity),
                        type=MovementType.IN,
                        reason=f"Sale #{sale_id} cancelled - reversal",
                    )
                    self.movement_repo.create(movement)

                    stock = self.stock_repo.first(product_id=item.product_id)
                    if stock:
                        stock.update_quantity(abs(item.quantity))
                        self.stock_repo.update(stock)

                self.session.commit()
            except Exception:
                self.session.rollback()
                raise

            items_data = [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                }
                for item in items
            ]

            EventBus.publish(
                SaleCancelled(
                    aggregate_id=sale.id,
                    sale_id=sale.id,
                    customer_id=sale.customer_id,
                    items=items_data,
                    reason=reason or "",
                    was_confirmed=True,
                    source="pos",
                )
            )
        else:
            # Simple cancel (DRAFT) — no inventory involved
            sale.cancel()
            self.sale_repo.update(sale)
            self.session.commit()

            EventBus.publish(
                SaleCancelled(
                    aggregate_id=sale.id,
                    sale_id=sale.id,
                    customer_id=sale.customer_id,
                    items=[],
                    reason=reason or "",
                    was_confirmed=False,
                    source="pos",
                )
            )

        return sale.dict()
