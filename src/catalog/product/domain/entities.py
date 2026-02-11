from dataclasses import dataclass
from datetime import datetime

from src.shared.domain.entities import Entity


@dataclass
class Category(Entity):
    name: str
    description: str | None
    id: int | None = None


@dataclass
class Product(Entity):
    name: str
    sku: str
    id: int | None = None
    description: str | None = None
    category_id: int | None = None
    created_at: datetime | None = None
