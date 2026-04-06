from collections.abc import Callable
from typing import Any

from src.shared.domain.events import DomainEvent
from src.shared.infra.events.event_bus import EventBus


def event_handler(event_type: type[DomainEvent]) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(event: DomainEvent, session: Any = None) -> None:
            func(event, session=session)

        wrapper.__name__ = func.__name__
        wrapper.__qualname__ = func.__qualname__
        EventBus.subscribe(event_type, wrapper)
        return func

    return decorator
