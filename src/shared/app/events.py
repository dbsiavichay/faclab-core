from abc import ABC, abstractmethod
from typing import Any

from src.shared.domain.events import DomainEvent


class EventPublisher(ABC):
    @abstractmethod
    def publish(self, event: DomainEvent, session: Any = None) -> None:
        raise NotImplementedError
