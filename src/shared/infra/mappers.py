from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar

E = TypeVar("E")  # Entity
M = TypeVar("M")  # Model


class Mapper(ABC, Generic[E, M]):
    """Base interface for all mappers in the application"""

    @abstractmethod
    def to_entity(self, model: Optional[M]) -> Optional[E]:
        """Converts an infrastructure model to a domain entity"""
        pass

    @abstractmethod
    def to_dict(self, entity: E) -> Dict[str, Any]:
        """Converts a domain entity to a dictionary for creating a model"""
        pass
