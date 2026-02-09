from typing import Callable, Type

from src.shared.domain.events import DomainEvent
from src.shared.infra.events.event_bus import EventBus


def event_handler(event_type: Type[DomainEvent]) -> Callable:
    def decorator(func: Callable) -> Callable:
        EventBus.subscribe(event_type, func)
        return func

    return decorator
