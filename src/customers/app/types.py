from decimal import Decimal
from typing import NotRequired, TypedDict


class CustomerBase(TypedDict):
    name: str
    tax_id: str
    tax_type: NotRequired[int]
    email: NotRequired[str]
    phone: NotRequired[str]
    address: NotRequired[str]
    city: NotRequired[str]
    state: NotRequired[str]
    country: NotRequired[str]
    credit_limit: NotRequired[Decimal]
    payment_terms: NotRequired[int]
    is_active: NotRequired[bool]


class CustomerInput(CustomerBase):
    pass


class CustomerOutput(CustomerBase):
    id: int


class CustomerContactBase(TypedDict):
    customer_id: int
    name: str
    role: NotRequired[str]
    email: NotRequired[str]
    phone: NotRequired[str]


class CustomerContactInput(CustomerContactBase):
    pass


class CustomerContactOutput(CustomerContactBase):
    id: int
