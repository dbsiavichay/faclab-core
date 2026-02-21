from wireup import injectable

from src.shared.app.events import EventPublisher
from src.shared.domain.events import DomainEvent
from src.shared.infra.events.event_bus import EventBus


@injectable(lifetime="singleton", as_type=EventPublisher)
class EventBusPublisher(EventPublisher):
    def publish(self, event: DomainEvent) -> None:
        EventBus.publish(event)
