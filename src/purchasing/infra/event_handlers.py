"""
Event handlers that react to purchasing domain events.
"""

import structlog

from src.inventory.movement.app.commands.movement import (
    CreateMovementCommand,
    CreateMovementCommandHandler,
)
from src.inventory.movement.domain.constants import MovementType
from src.purchasing.domain.events import PurchaseOrderReceived
from src.shared.infra.events.decorators import event_handler

logger = structlog.get_logger(__name__)


@event_handler(PurchaseOrderReceived)
def handle_purchase_order_received(event: PurchaseOrderReceived) -> None:
    """
    When goods are received for a purchase order, create IN inventory movements.
    Each receipt item becomes an individual IN movement.
    """
    logger.info(
        "handling_purchase_order_received",
        purchase_order_id=event.purchase_order_id,
        order_number=event.order_number,
        is_complete=event.is_complete,
        item_count=len(event.items),
    )

    from src import wireup_container

    with wireup_container.enter_scope() as scope:
        try:
            for item in event.items:
                handler = scope.get(CreateMovementCommandHandler)

                command = CreateMovementCommand(
                    product_id=item["product_id"],
                    quantity=abs(item["quantity"]),
                    type=MovementType.IN.value,
                    location_id=item.get("location_id"),
                    reference_type="purchase_order",
                    reference_id=event.purchase_order_id,
                    reason=f"Purchase order {event.order_number} received",
                )

                handler.handle(command)
                logger.info(
                    "in_movement_created",
                    purchase_order_id=event.purchase_order_id,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                )

        except Exception as e:
            logger.error(
                "purchase_order_received_handler_error",
                purchase_order_id=event.purchase_order_id,
                error=str(e),
            )
            raise
