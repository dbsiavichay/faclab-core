from collections import defaultdict
from collections.abc import Callable

import structlog

from src.shared.domain.events import DomainEvent

logger = structlog.get_logger(__name__)


class EventBus:
    _subscribers: dict[type[DomainEvent], list[Callable]] = defaultdict(list)

    @classmethod
    def subscribe(cls, event_type: type[DomainEvent], handler: Callable) -> None:
        cls._subscribers[event_type].append(handler)

    @classmethod
    def publish(cls, event: DomainEvent) -> None:
        event_type = type(event)
        handlers = cls._subscribers.get(event_type, [])
        logger.info(
            "event_published",
            event_type=event_type.__name__,
            handler_count=len(handlers),
        )
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    "event_handler_error",
                    handler=handler.__name__,
                    event_type=event_type.__name__,
                    error=str(e),
                )

    @classmethod
    def clear(cls) -> None:
        cls._subscribers.clear()
