"""
Event handlers para Stock que reaccionan a eventos de otros módulos.
Este handler desacopla Movement de Stock mediante eventos.
"""

import structlog

from src.inventory.movement.domain.events import MovementCreated
from src.inventory.stock.domain.entities import Stock
from src.inventory.stock.domain.events import StockCreated, StockUpdated
from src.shared.app.repositories import Repository
from src.shared.infra.events.decorators import event_handler
from src.shared.infra.events.event_bus import EventBus

logger = structlog.get_logger(__name__)


@event_handler(MovementCreated)
def handle_movement_created(event: MovementCreated) -> None:
    """
    Cuando se crea un movimiento, actualizar o crear el stock correspondiente.
    """
    logger.info(
        "handling_movement_created",
        movement_id=event.aggregate_id,
        product_id=event.product_id,
        quantity=event.quantity,
    )

    from src import wireup_container

    with wireup_container.enter_scope() as scope:
        try:
            stock_repo = scope.get(Repository[Stock])
            stock = stock_repo.first(product_id=event.product_id)

            if stock is None:
                logger.info(
                    "creating_new_stock",
                    product_id=event.product_id,
                )
                stock = Stock(product_id=event.product_id, quantity=event.quantity)
                stock = stock_repo.create(stock)

                EventBus.publish(
                    StockCreated(
                        aggregate_id=stock.id,
                        product_id=stock.product_id,
                        quantity=stock.quantity,
                        location=stock.location,
                    )
                )
                logger.info(
                    "stock_created",
                    stock_id=stock.id,
                    product_id=stock.product_id,
                    quantity=stock.quantity,
                )
            else:
                old_quantity = stock.quantity
                logger.info(
                    "updating_existing_stock",
                    stock_id=stock.id,
                    current_quantity=old_quantity,
                    delta=event.quantity,
                )

                stock.update_quantity(event.quantity)
                stock = stock_repo.update(stock)

                EventBus.publish(
                    StockUpdated(
                        aggregate_id=stock.id,
                        product_id=stock.product_id,
                        old_quantity=old_quantity,
                        new_quantity=stock.quantity,
                        location=stock.location,
                    )
                )
                logger.info(
                    "stock_updated",
                    stock_id=stock.id,
                    old_quantity=old_quantity,
                    new_quantity=stock.quantity,
                )

        except Exception as e:
            logger.error(
                "movement_created_handler_error",
                movement_id=event.aggregate_id,
                product_id=event.product_id,
                error=str(e),
            )
            raise
