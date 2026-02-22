from dataclasses import dataclass

from src.shared.domain.entities import Entity


@dataclass
class UnitOfMeasure(Entity):
    name: str
    symbol: str
    id: int | None = None
    description: str | None = None
    is_active: bool = True
