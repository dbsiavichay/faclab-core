from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.shared.domain.entities import Entity


@dataclass
class Category(Entity):
    name: str
    description: Optional[str]
    id: Optional[int] = None


@dataclass
class Product(Entity):
    name: str
    sku: str
    id: Optional[int] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    created_at: Optional[datetime] = None
