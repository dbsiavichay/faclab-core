from dataclasses import dataclass
from typing import Any, Dict

import pytest

from src.shared.domain.events import DomainEvent
from src.shared.infra.events.event_bus import EventBus


@dataclass
class OrderCreated(DomainEvent):
    order_total: float = 0.0

    def _payload(self) -> Dict[str, Any]:
        return {"order_total": self.order_total}


@pytest.fixture(autouse=True)
def clear_event_bus():
    EventBus.clear()
    yield
    EventBus.clear()


def test_subscribe_and_publish():
    results = []

    def handler(event: OrderCreated):
        results.append(event.order_total)

    EventBus.subscribe(OrderCreated, handler)
    EventBus.publish(OrderCreated(aggregate_id=1, order_total=100.0))

    assert results == [100.0]


def test_publish_without_subscribers():
    EventBus.publish(OrderCreated(aggregate_id=1, order_total=50.0))


def test_handler_error_does_not_stop_others():
    results = []

    def failing_handler(event: OrderCreated):
        raise RuntimeError("handler failed")

    def working_handler(event: OrderCreated):
        results.append(event.order_total)

    EventBus.subscribe(OrderCreated, failing_handler)
    EventBus.subscribe(OrderCreated, working_handler)
    EventBus.publish(OrderCreated(aggregate_id=1, order_total=75.0))

    assert results == [75.0]


def test_clear_removes_all():
    results = []

    def handler(event: OrderCreated):
        results.append(event.order_total)

    EventBus.subscribe(OrderCreated, handler)
    EventBus.clear()
    EventBus.publish(OrderCreated(aggregate_id=1, order_total=25.0))

    assert results == []


def test_event_to_dict():
    event = OrderCreated(aggregate_id=42, order_total=99.99)
    d = event.to_dict()

    assert d["event_type"] == "OrderCreated"
    assert d["aggregate_id"] == 42
    assert d["payload"] == {"order_total": 99.99}
    assert "event_id" in d
    assert "occurred_at" in d
