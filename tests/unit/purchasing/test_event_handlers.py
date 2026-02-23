from unittest.mock import MagicMock, Mock, patch

from src.purchasing.domain.events import PurchaseOrderReceived


@patch("src.wireup_container")
def test_handle_purchase_order_received_creates_movements(mock_container):
    """
    Verifies that handle_purchase_order_received creates one IN movement
    per item in the event payload.
    """
    from src.inventory.movement.app.commands.movement import CreateMovementCommand
    from src.inventory.movement.domain.constants import MovementType
    from src.purchasing.infra import event_handlers  # noqa: F401 (registers handler)

    items = [
        {"product_id": 5, "quantity": 10, "location_id": None},
        {"product_id": 6, "quantity": 3, "location_id": 2},
    ]

    mock_handler = MagicMock()
    mock_scope = Mock()
    mock_scope.get.return_value = mock_handler
    mock_container.enter_scope.return_value.__enter__.return_value = mock_scope

    event = PurchaseOrderReceived(
        aggregate_id=1,
        purchase_order_id=1,
        order_number="PO-2026-0001",
        is_complete=True,
        items=items,
    )

    from src.purchasing.infra.event_handlers import handle_purchase_order_received

    handle_purchase_order_received(event)

    assert mock_handler.handle.call_count == 2

    first_call = mock_handler.handle.call_args_list[0][0][0]
    assert isinstance(first_call, CreateMovementCommand)
    assert first_call.product_id == 5
    assert first_call.quantity == 10
    assert first_call.type == MovementType.IN.value
    assert first_call.reference_type == "purchase_order"
    assert first_call.reference_id == 1

    second_call = mock_handler.handle.call_args_list[1][0][0]
    assert second_call.product_id == 6
    assert second_call.quantity == 3
    assert second_call.location_id == 2
