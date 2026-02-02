from datetime import datetime
from typing import NotRequired, TypedDict


class MovementInput(TypedDict):
    product_id: int
    quantity: int
    type: str
    reason: NotRequired[str]
    date: NotRequired[datetime]


class MovementOutput(MovementInput):
    id: int
