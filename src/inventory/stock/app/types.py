from typing import NotRequired, TypedDict


class StockOutput(TypedDict):
    id: int
    product_id: int
    quantity: int
    location: NotRequired[str]
