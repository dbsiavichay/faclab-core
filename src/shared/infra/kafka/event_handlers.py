import structlog

from src.sales.domain.events import SaleConfirmed
from src.shared.infra.events.decorators import event_handler
from src.shared.infra.kafka.producer import KafkaEventProducer

logger = structlog.get_logger(__name__)

_producer: KafkaEventProducer | None = None


def _get_producer() -> KafkaEventProducer | None:
    global _producer
    if _producer is None:
        from config import config

        if not config.KAFKA_ENABLED:
            return None

        _producer = KafkaEventProducer(config.KAFKA_BOOTSTRAP_SERVERS)
        _producer.start()

    return _producer


@event_handler(SaleConfirmed)
def publish_sale_confirmed_to_kafka(event: SaleConfirmed) -> None:
    producer = _get_producer()
    if producer is None:
        return
    producer.send("sales.confirmed", event)
