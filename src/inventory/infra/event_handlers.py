"""
Event handlers que reaccionan a eventos de otros módulos.
Estos handlers permiten el desacoplamiento entre módulos vía eventos.
"""

import logging

from src.inventory.movement.app.commands import (
    CreateMovementCommand,
    CreateMovementCommandHandler,
)
from src.inventory.movement.domain.constants import MovementType
from src.sales.domain.events import SaleCancelled, SaleConfirmed
from src.shared.infra.events.decorators import event_handler

logger = logging.getLogger(__name__)


@event_handler(SaleConfirmed)
def handle_sale_confirmed(event: SaleConfirmed) -> None:
    """
    Cuando se confirma una venta, crear movimientos OUT de inventario.
    Este handler desacopla el módulo de sales del módulo de inventory.
    """
    logger.info(f"Handling SaleConfirmed event for sale_id={event.sale_id}")

    # Resolver el command handler del container
    from src import container

    try:
        # Crear movimientos OUT para cada item de la venta
        for item in event.items:
            # Obtener el command handler (SCOPED - con nueva sesión)
            handler = container.resolve(CreateMovementCommandHandler)

            # Crear comando de movimiento OUT (cantidad negativa)
            command = CreateMovementCommand(
                product_id=item["product_id"],
                quantity=-abs(item["quantity"]),  # Asegurar que sea negativo
                type=MovementType.OUT.value,
                reason=f"Sale #{event.sale_id} confirmed",
            )

            handler.handle(command)
            logger.info(
                f"Created OUT movement for product_id={item['product_id']}, "
                f"quantity={item['quantity']}"
            )

    except Exception as e:
        logger.error(
            f"Error handling SaleConfirmed event for sale_id={event.sale_id}: {e}"
        )
        # En producción, aquí se podría implementar retry logic o dead letter queue
        raise


@event_handler(SaleCancelled)
def handle_sale_cancelled(event: SaleCancelled) -> None:
    """
    Cuando se cancela una venta, revertir movimientos si la venta estaba confirmada.
    Solo crea movimientos IN si was_confirmed=True.
    """
    logger.info(
        f"Handling SaleCancelled event for sale_id={event.sale_id}, "
        f"was_confirmed={event.was_confirmed}"
    )

    # Solo revertir si la venta estaba confirmada
    if not event.was_confirmed:
        logger.info(
            f"Sale {event.sale_id} was not confirmed, no inventory reversal needed"
        )
        return

    # Resolver el command handler del container
    from src import container

    try:
        # Crear movimientos IN de reversión para cada item
        for item in event.items:
            # Obtener el command handler
            handler = container.resolve(CreateMovementCommandHandler)

            # Crear comando de movimiento IN (cantidad positiva)
            command = CreateMovementCommand(
                product_id=item["product_id"],
                quantity=abs(item["quantity"]),  # Asegurar que sea positivo
                type=MovementType.IN.value,
                reason=f"Sale #{event.sale_id} cancelled - reversal",
            )

            handler.handle(command)
            logger.info(
                f"Created IN reversal movement for product_id={item['product_id']}, "
                f"quantity={item['quantity']}"
            )

    except Exception as e:
        logger.error(
            f"Error handling SaleCancelled event for sale_id={event.sale_id}: {e}"
        )
        raise
