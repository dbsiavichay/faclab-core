"""
Event handlers para Stock que reaccionan a eventos de otros módulos.
Este handler desacopla Movement de Stock mediante eventos.
"""

import logging

from src.inventory.movement.domain.events import MovementCreated
from src.inventory.stock.domain.entities import Stock
from src.inventory.stock.domain.events import StockCreated, StockUpdated
from src.shared.app.repositories import Repository
from src.shared.infra.events.decorators import event_handler
from src.shared.infra.events.event_bus import EventBus

logger = logging.getLogger(__name__)


@event_handler(MovementCreated)
def handle_movement_created(event: MovementCreated) -> None:
    """
    Cuando se crea un movimiento, actualizar o crear el stock correspondiente.
    Este handler desacopla Movement de Stock completamente.

    Flujo:
    1. Buscar stock existente para el producto
    2. Si no existe, crear nuevo stock con la cantidad del movimiento
    3. Si existe, actualizar la cantidad del stock
    4. Publicar evento StockCreated o StockUpdated según corresponda
    """
    logger.info(
        f"Handling MovementCreated event: movement_id={event.aggregate_id}, "
        f"product_id={event.product_id}, quantity={event.quantity}"
    )

    # Resolver el repositorio del wireup container
    from src import wireup_container

    # Crear un scope para resolver injectables SCOPED
    # Los event handlers se ejecutan fuera del contexto de request HTTP,
    # por lo que necesitamos crear un scope manualmente
    with wireup_container.enter_scope() as scope:
        try:
            # Obtener repositorio de Stock dentro del scope
            stock_repo = scope.get(Repository[Stock])

            # Buscar stock existente
            stock = stock_repo.first(product_id=event.product_id)

            if stock is None:
                # Crear nuevo stock
                logger.info(
                    f"No existing stock for product_id={event.product_id}, creating new stock"
                )
                stock = Stock(product_id=event.product_id, quantity=event.quantity)
                stock = stock_repo.create(stock)

                # Publicar evento StockCreated
                EventBus.publish(
                    StockCreated(
                        aggregate_id=stock.id,
                        product_id=stock.product_id,
                        quantity=stock.quantity,
                        location=stock.location,
                    )
                )
                logger.info(
                    f"Created stock: stock_id={stock.id}, "
                    f"product_id={stock.product_id}, quantity={stock.quantity}"
                )
            else:
                # Actualizar stock existente
                logger.info(
                    f"Updating existing stock: stock_id={stock.id}, "
                    f"current_quantity={stock.quantity}, delta={event.quantity}"
                )
                old_quantity = stock.quantity

                # update_quantity valida stock insuficiente (raises InsufficientStock)
                stock.update_quantity(event.quantity)
                stock = stock_repo.update(stock)

                # Publicar evento StockUpdated
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
                    f"Updated stock: stock_id={stock.id}, "
                    f"old_quantity={old_quantity}, new_quantity={stock.quantity}"
                )

        except Exception as e:
            logger.error(
                f"Error handling MovementCreated event for "
                f"movement_id={event.aggregate_id}, product_id={event.product_id}: {e}"
            )
            # En producción, aquí se podría implementar retry logic o dead letter queue
            raise
