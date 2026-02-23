"""
Event handlers for Lot that react to purchasing domain events.
Creates or updates lots when purchase orders are received.
"""

import structlog

from src.purchasing.domain.events import PurchaseOrderReceived
from src.shared.infra.events.decorators import event_handler

logger = structlog.get_logger(__name__)


@event_handler(PurchaseOrderReceived)
def handle_purchase_order_received_lots(event: PurchaseOrderReceived) -> None:
    """
    When goods are received for a purchase order, create or update lots.
    Only processes items that include a lot_number.
    """
    items_with_lots = [item for item in event.items if item.get("lot_number")]
    if not items_with_lots:
        return

    logger.info(
        "handling_purchase_order_received_lots",
        purchase_order_id=event.purchase_order_id,
        items_with_lots=len(items_with_lots),
    )

    from src import wireup_container

    with wireup_container.enter_scope() as scope:
        try:
            from dataclasses import replace

            from src.inventory.lot.domain.entities import Lot, MovementLotItem
            from src.inventory.movement.domain.entities import Movement
            from src.shared.app.repositories import Repository

            lot_repo = scope.get(Repository[Lot])
            movement_lot_item_repo = scope.get(Repository[MovementLotItem])
            movement_repo = scope.get(Repository[Movement])

            for item in items_with_lots:
                product_id = item["product_id"]
                lot_number = item["lot_number"]
                quantity = item["quantity"]

                # Find existing lot or create new one
                existing_lot = lot_repo.first(
                    product_id=product_id, lot_number=lot_number
                )

                if existing_lot is None:
                    lot = Lot(
                        product_id=product_id,
                        lot_number=lot_number,
                        initial_quantity=quantity,
                        current_quantity=quantity,
                    )
                    lot = lot_repo.create(lot)
                    logger.info(
                        "lot_created",
                        lot_id=lot.id,
                        product_id=product_id,
                        lot_number=lot_number,
                        quantity=quantity,
                    )
                else:
                    lot = replace(
                        existing_lot,
                        current_quantity=existing_lot.current_quantity + quantity,
                    )
                    lot = lot_repo.update(lot)
                    logger.info(
                        "lot_updated",
                        lot_id=lot.id,
                        product_id=product_id,
                        lot_number=lot_number,
                        new_quantity=lot.current_quantity,
                    )

                # Find the movement created for this item and link it
                movements = movement_repo.filter_by(
                    reference_type="purchase_order",
                    reference_id=event.purchase_order_id,
                    product_id=product_id,
                )
                if movements:
                    movement = movements[-1]
                    movement_lot_item = MovementLotItem(
                        movement_id=movement.id,
                        lot_id=lot.id,
                        quantity=quantity,
                    )
                    movement_lot_item_repo.create(movement_lot_item)
                    logger.info(
                        "movement_lot_item_created",
                        movement_id=movement.id,
                        lot_id=lot.id,
                        quantity=quantity,
                    )

        except Exception as e:
            logger.error(
                "purchase_order_received_lots_handler_error",
                purchase_order_id=event.purchase_order_id,
                error=str(e),
            )
            raise
