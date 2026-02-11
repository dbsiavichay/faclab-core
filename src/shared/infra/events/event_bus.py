import logging
from collections import defaultdict
from collections.abc import Callable

from src.shared.domain.events import DomainEvent

logger = logging.getLogger(__name__)


class EventBus:
    _subscribers: dict[type[DomainEvent], list[Callable]] = defaultdict(list)

    @classmethod
    def subscribe(cls, event_type: type[DomainEvent], handler: Callable) -> None:
        cls._subscribers[event_type].append(handler)

    @classmethod
    def publish(cls, event: DomainEvent) -> None:
        event_type = type(event)
        handlers = cls._subscribers.get(event_type, [])
        logger.info(f"Publishing {event_type.__name__} to {len(handlers)} handler(s)")
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    f"Error in handler {handler.__name__} for "
                    f"{event_type.__name__}: {e}"
                )

    @classmethod
    def clear(cls) -> None:
        cls._subscribers.clear()
