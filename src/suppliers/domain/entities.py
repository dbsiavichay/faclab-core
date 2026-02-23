from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.customers.domain.entities import TaxType
from src.shared.domain.entities import Entity


@dataclass
class Supplier(Entity):
    name: str
    tax_id: str
    id: int | None = None
    tax_type: TaxType = TaxType.RUC
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    payment_terms: int | None = None  # Credit days
    lead_time_days: int | None = None
    is_active: bool = True
    notes: str | None = None
    created_at: datetime | None = None


@dataclass
class SupplierContact(Entity):
    supplier_id: int
    name: str
    id: int | None = None
    role: str | None = None
    email: str | None = None
    phone: str | None = None


@dataclass
class SupplierProduct(Entity):
    supplier_id: int
    product_id: int
    purchase_price: Decimal
    id: int | None = None
    supplier_sku: str | None = None
    min_order_quantity: int = 1
    lead_time_days: int | None = None
    is_preferred: bool = False
