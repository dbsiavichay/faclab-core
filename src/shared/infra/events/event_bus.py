from collections import defaultdict
from collections.abc import Callable

import structlog
from opentelemetry import trace

from src.shared.domain.events import DomainEvent
from src.shared.infra.telemetry_instruments import (
    event_handler_errors,
    events_published,
)

logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)


class EventBus:
    _subscribers: dict[type[DomainEvent], list[Callable]] = defaultdict(list)

    @classmethod
    def subscribe(cls, event_type: type[DomainEvent], handler: Callable) -> None:
        cls._subscribers[event_type].append(handler)

    @classmethod
    def publish(cls, event: DomainEvent) -> None:
        event_type = type(event)
        event_type_name = event_type.__name__
        handlers = cls._subscribers.get(event_type, [])

        with tracer.start_as_current_span(
            f"event.publish.{event_type_name}",
            attributes={
                "event.type": event_type_name,
                "event.handler_count": len(handlers),
            },
        ):
            logger.info(
                "event_published",
                event_type=event_type_name,
                handler_count=len(handlers),
            )
            events_published.add(1, {"event.type": event_type_name})

            for handler in handlers:
                handler_name = handler.__name__
                with tracer.start_as_current_span(
                    f"event.handle.{handler_name}",
                    attributes={
                        "event.type": event_type_name,
                        "event.handler": handler_name,
                    },
                ) as span:
                    try:
                        handler(event)
                        span.set_status(trace.StatusCode.OK)
                    except Exception as e:
                        logger.error(
                            "event_handler_error",
                            handler=handler_name,
                            event_type=event_type_name,
                            error=str(e),
                        )
                        event_handler_errors.add(
                            1,
                            {
                                "event.type": event_type_name,
                                "event.handler": handler_name,
                            },
                        )
                        span.set_status(trace.StatusCode.ERROR, str(e))
                        span.record_exception(e)

    @classmethod
    def clear(cls) -> None:
        cls._subscribers.clear()
