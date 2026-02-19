from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from src.inventory.stock.domain.entities import Stock
from src.sales.domain.entities import Sale, SaleItem, SaleStatus
from src.sales.domain.exceptions import InsufficientStockError, SaleHasNoItemsError
from src.shared.infra.events.event_bus import EventBus
from src.shared.infra.exceptions import NotFoundError


@pytest.fixture(autouse=True)
def clear_event_bus():
    EventBus.clear()
    yield
    EventBus.clear()


def _make_sale(**overrides) -> Sale:
    defaults = {
        "id": 1,
        "customer_id": 10,
        "status": SaleStatus.DRAFT,
        "subtotal": Decimal("1000"),
        "total": Decimal("1000"),
    }
    defaults.update(overrides)
    return Sale(**defaults)


def _make_sale_item(**overrides) -> SaleItem:
    defaults = {
        "id": 1,
        "sale_id": 1,
        "product_id": 100,
        "quantity": 5,
        "unit_price": Decimal("200.00"),
        "discount": Decimal("0"),
    }
    defaults.update(overrides)
    return SaleItem(**defaults)


def _make_stock(**overrides) -> Stock:
    defaults = {
        "id": 1,
        "product_id": 100,
        "quantity": 50,
    }
    defaults.update(overrides)
    return Stock(**defaults)


def _build_confirm_service(sale=None, items=None, stock=None, session=None):
    """Build a ConfirmSaleService with mocked repos"""
    from src.pos.sales.app.services import ConfirmSaleService

    session = session or MagicMock()
    sale_mapper = MagicMock()
    sale_item_mapper = MagicMock()
    movement_mapper = MagicMock()
    stock_mapper = MagicMock()

    service = ConfirmSaleService(
        session=session,
        sale_mapper=sale_mapper,
        sale_item_mapper=sale_item_mapper,
        movement_mapper=movement_mapper,
        stock_mapper=stock_mapper,
    )

    # Mock repos
    service.sale_repo = MagicMock()
    service.sale_item_repo = MagicMock()
    service.movement_repo = MagicMock()
    service.stock_repo = MagicMock()

    if sale is not None:
        service.sale_repo.get_by_id.return_value = sale
        service.sale_repo.update.return_value = sale
    if items is not None:
        service.sale_item_repo.filter_by.return_value = items
    if stock is not None:
        service.stock_repo.first.return_value = stock

    return service


def _build_cancel_service(sale=None, items=None, stock=None, session=None):
    """Build a CancelSaleService with mocked repos"""
    from src.pos.sales.app.services import CancelSaleService

    session = session or MagicMock()
    sale_mapper = MagicMock()
    sale_item_mapper = MagicMock()
    movement_mapper = MagicMock()
    stock_mapper = MagicMock()

    service = CancelSaleService(
        session=session,
        sale_mapper=sale_mapper,
        sale_item_mapper=sale_item_mapper,
        movement_mapper=movement_mapper,
        stock_mapper=stock_mapper,
    )

    # Mock repos
    service.sale_repo = MagicMock()
    service.sale_item_repo = MagicMock()
    service.movement_repo = MagicMock()
    service.stock_repo = MagicMock()

    if sale is not None:
        service.sale_repo.get_by_id.return_value = sale
        service.sale_repo.update.return_value = sale
    if items is not None:
        service.sale_item_repo.filter_by.return_value = items
    if stock is not None:
        service.stock_repo.first.return_value = stock

    return service


# === ConfirmSaleService Tests ===


class TestConfirmSaleService:
    def test_confirm_happy_path(self):
        sale = _make_sale()
        items = [_make_sale_item()]
        stock = _make_stock(quantity=50)
        session = MagicMock()

        service = _build_confirm_service(
            sale=sale, items=items, stock=stock, session=session
        )

        result = service.execute(sale_id=1)

        assert result["status"] == SaleStatus.CONFIRMED
        session.commit.assert_called_once()
        service.sale_repo.update.assert_called_once()
        service.movement_repo.create.assert_called_once()
        service.stock_repo.update.assert_called_once()

    def test_confirm_insufficient_stock_raises_error(self):
        sale = _make_sale()
        items = [_make_sale_item(quantity=10)]
        stock = _make_stock(quantity=3)  # Not enough
        session = MagicMock()

        service = _build_confirm_service(
            sale=sale, items=items, stock=stock, session=session
        )

        with pytest.raises(InsufficientStockError):
            service.execute(sale_id=1)

        session.commit.assert_not_called()
        session.rollback.assert_not_called()

    def test_confirm_no_stock_record_raises_error(self):
        sale = _make_sale()
        items = [_make_sale_item(quantity=5)]
        session = MagicMock()

        service = _build_confirm_service(
            sale=sale, items=items, stock=None, session=session
        )
        service.stock_repo.first.return_value = None

        with pytest.raises(InsufficientStockError):
            service.execute(sale_id=1)

    def test_confirm_no_items_raises_error(self):
        sale = _make_sale()
        session = MagicMock()

        service = _build_confirm_service(sale=sale, items=[], session=session)

        with pytest.raises(SaleHasNoItemsError):
            service.execute(sale_id=1)

    def test_confirm_sale_not_found_raises_error(self):
        session = MagicMock()

        service = _build_confirm_service(sale=None, session=session)
        service.sale_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            service.execute(sale_id=999)

    def test_confirm_rollback_on_unexpected_error(self):
        sale = _make_sale()
        items = [_make_sale_item()]
        stock = _make_stock(quantity=50)
        session = MagicMock()

        service = _build_confirm_service(
            sale=sale, items=items, stock=stock, session=session
        )
        service.movement_repo.create.side_effect = RuntimeError("DB error")

        with pytest.raises(RuntimeError, match="DB error"):
            service.execute(sale_id=1)

        session.rollback.assert_called_once()
        session.commit.assert_not_called()

    def test_confirm_publishes_event_with_pos_source(self):
        published_events = []
        from src.sales.domain.events import SaleConfirmed

        EventBus.subscribe(SaleConfirmed, lambda e: published_events.append(e))

        sale = _make_sale()
        items = [_make_sale_item()]
        stock = _make_stock(quantity=50)
        session = MagicMock()

        service = _build_confirm_service(
            sale=sale, items=items, stock=stock, session=session
        )
        service.execute(sale_id=1)

        assert len(published_events) == 1
        assert published_events[0].source == "pos"

    def test_confirm_multiple_items(self):
        sale = _make_sale()
        items = [
            _make_sale_item(id=1, product_id=100, quantity=3),
            _make_sale_item(id=2, product_id=200, quantity=2),
        ]
        stock = _make_stock(quantity=50)
        session = MagicMock()

        service = _build_confirm_service(
            sale=sale, items=items, stock=stock, session=session
        )
        result = service.execute(sale_id=1)

        assert result["status"] == SaleStatus.CONFIRMED
        assert service.movement_repo.create.call_count == 2
        assert service.stock_repo.update.call_count == 2
        session.commit.assert_called_once()


# === CancelSaleService Tests ===


class TestCancelSaleService:
    def test_cancel_draft_sale(self):
        sale = _make_sale(status=SaleStatus.DRAFT)
        session = MagicMock()

        service = _build_cancel_service(sale=sale, session=session)
        result = service.execute(sale_id=1)

        assert result["status"] == SaleStatus.CANCELLED
        session.commit.assert_called_once()
        # No inventory operations for DRAFT
        service.movement_repo.create.assert_not_called()
        service.stock_repo.update.assert_not_called()

    def test_cancel_confirmed_sale_reverses_inventory(self):
        sale = _make_sale(status=SaleStatus.CONFIRMED)
        items = [_make_sale_item()]
        stock = _make_stock(quantity=45)
        session = MagicMock()

        service = _build_cancel_service(
            sale=sale, items=items, stock=stock, session=session
        )
        result = service.execute(sale_id=1)

        assert result["status"] == SaleStatus.CANCELLED
        session.commit.assert_called_once()
        service.movement_repo.create.assert_called_once()
        service.stock_repo.update.assert_called_once()

    def test_cancel_sale_not_found(self):
        session = MagicMock()

        service = _build_cancel_service(sale=None, session=session)
        service.sale_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            service.execute(sale_id=999)

    def test_cancel_confirmed_rollback_on_error(self):
        sale = _make_sale(status=SaleStatus.CONFIRMED)
        items = [_make_sale_item()]
        stock = _make_stock(quantity=45)
        session = MagicMock()

        service = _build_cancel_service(
            sale=sale, items=items, stock=stock, session=session
        )
        service.movement_repo.create.side_effect = RuntimeError("DB error")

        with pytest.raises(RuntimeError, match="DB error"):
            service.execute(sale_id=1)

        session.rollback.assert_called_once()

    def test_cancel_publishes_event_with_pos_source(self):
        published_events = []
        from src.sales.domain.events import SaleCancelled

        EventBus.subscribe(SaleCancelled, lambda e: published_events.append(e))

        sale = _make_sale(status=SaleStatus.CONFIRMED)
        items = [_make_sale_item()]
        stock = _make_stock(quantity=45)
        session = MagicMock()

        service = _build_cancel_service(
            sale=sale, items=items, stock=stock, session=session
        )
        service.execute(sale_id=1)

        assert len(published_events) == 1
        assert published_events[0].source == "pos"
        assert published_events[0].was_confirmed is True

    def test_cancel_draft_publishes_event_with_pos_source(self):
        published_events = []
        from src.sales.domain.events import SaleCancelled

        EventBus.subscribe(SaleCancelled, lambda e: published_events.append(e))

        sale = _make_sale(status=SaleStatus.DRAFT)
        session = MagicMock()

        service = _build_cancel_service(sale=sale, session=session)
        service.execute(sale_id=1)

        assert len(published_events) == 1
        assert published_events[0].source == "pos"
        assert published_events[0].was_confirmed is False


# === Event Handler Guard Tests ===


class TestEventHandlerGuards:
    def test_sale_confirmed_pos_source_skips_inventory(self):
        from src.inventory.infra.event_handlers import handle_sale_confirmed
        from src.sales.domain.events import SaleConfirmed

        event = SaleConfirmed(
            aggregate_id=1,
            sale_id=1,
            customer_id=10,
            items=[{"product_id": 100, "quantity": 5}],
            total=1000.0,
            source="pos",
        )

        # Should not raise or call wireup_container
        handle_sale_confirmed(event)

    def test_sale_cancelled_pos_source_skips_inventory(self):
        from src.inventory.infra.event_handlers import handle_sale_cancelled
        from src.sales.domain.events import SaleCancelled

        event = SaleCancelled(
            aggregate_id=1,
            sale_id=1,
            customer_id=10,
            items=[{"product_id": 100, "quantity": 5}],
            reason="test",
            was_confirmed=True,
            source="pos",
        )

        # Should not raise or call wireup_container
        handle_sale_cancelled(event)

    def test_sale_confirmed_admin_source_processes_normally(self):
        """Admin source events should attempt to process (will fail without wireup_container)"""
        from src.inventory.infra.event_handlers import handle_sale_confirmed
        from src.sales.domain.events import SaleConfirmed

        event = SaleConfirmed(
            aggregate_id=1,
            sale_id=1,
            customer_id=10,
            items=[{"product_id": 100, "quantity": 5}],
            total=1000.0,
            source="admin",
        )

        # Admin source should try to process — will fail because wireup_container is None
        # This proves the guard is NOT skipping admin events
        with pytest.raises((AttributeError, TypeError)):
            handle_sale_confirmed(event)

    def test_sale_confirmed_default_source_is_admin(self):
        from src.sales.domain.events import SaleConfirmed

        event = SaleConfirmed(aggregate_id=1, sale_id=1)
        assert event.source == "admin"

    def test_sale_cancelled_default_source_is_admin(self):
        from src.sales.domain.events import SaleCancelled

        event = SaleCancelled(aggregate_id=1, sale_id=1)
        assert event.source == "admin"
