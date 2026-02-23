"""
Event handlers for Serial Numbers that react to purchasing domain events.
Creates serial numbers when purchase orders are received.
"""

import structlog

from src.purchasing.domain.events import PurchaseOrderReceived
from src.shared.infra.events.decorators import event_handler

logger = structlog.get_logger(__name__)


@event_handler(PurchaseOrderReceived)
def handle_purchase_order_received_serials(event: PurchaseOrderReceived) -> None:
    """
    When goods are received for a purchase order, create serial numbers.
    Only processes items that include serial_numbers list.
    """
    items_with_serials = [item for item in event.items if item.get("serial_numbers")]
    if not items_with_serials:
        return

    logger.info(
        "handling_purchase_order_received_serials",
        purchase_order_id=event.purchase_order_id,
        items_with_serials=len(items_with_serials),
    )

    from src import wireup_container

    with wireup_container.enter_scope() as scope:
        try:
            from src.inventory.lot.domain.entities import Lot
            from src.inventory.serial.domain.entities import SerialNumber, SerialStatus
            from src.shared.app.repositories import Repository

            serial_repo = scope.get(Repository[SerialNumber])
            lot_repo = scope.get(Repository[Lot])

            for item in items_with_serials:
                product_id = item["product_id"]
                serial_numbers = item.get("serial_numbers", [])
                lot_number = item.get("lot_number")
                location_id = item.get("location_id")
                purchase_order_id = item.get(
                    "purchase_order_id", event.purchase_order_id
                )

                # Resolve lot_id if lot_number is provided
                lot_id = None
                if lot_number:
                    lot = lot_repo.first(product_id=product_id, lot_number=lot_number)
                    if lot is not None:
                        lot_id = lot.id

                for sn in serial_numbers:
                    existing = serial_repo.first(serial_number=sn)
                    if existing is not None:
                        logger.warning(
                            "serial_number_already_exists",
                            serial_number=sn,
                            product_id=product_id,
                        )
                        continue

                    serial = SerialNumber(
                        product_id=product_id,
                        serial_number=sn,
                        status=SerialStatus.AVAILABLE,
                        lot_id=lot_id,
                        location_id=location_id,
                        purchase_order_id=purchase_order_id,
                    )
                    serial = serial_repo.create(serial)
                    logger.info(
                        "serial_number_created",
                        serial_id=serial.id,
                        serial_number=sn,
                        product_id=product_id,
                        lot_id=lot_id,
                    )

        except Exception as e:
            logger.error(
                "purchase_order_received_serials_handler_error",
                purchase_order_id=event.purchase_order_id,
                error=str(e),
            )
            raise
