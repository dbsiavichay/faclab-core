from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import IntEnum
from typing import Optional

from src.shared.domain.entities import Entity


class TaxType(IntEnum):
    RUC = 1
    NATIONAL_ID = 2  # Cédula
    PASSPORT = 3  # Pasaporte
    FOREIGN_ID = 4  # Identificación de extranjero


@dataclass
class Customer(Entity):
    name: str
    tax_id: str
    tax_type: TaxType = TaxType.RUC
    id: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    payment_terms: Optional[int] = None  # Days
    is_active: bool = True
    created_at: Optional[datetime] = None


@dataclass
class CustomerContact(Entity):
    customer_id: int
    name: str
    id: Optional[int] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
