from src.shared.domain.exceptions import BaseError


class InsufficientStockError(BaseError):
    def __init__(self, product_id: int, quantity: int):
        self.status_code = 400
        self.data = {}
        self.data["product_id"] = product_id
        self.data["quantity"] = quantity
        self.message = (
            f"Insufficient stock for product {product_id} with quantity {quantity}"
        )
        super().__init__(self.status_code, self.message)
