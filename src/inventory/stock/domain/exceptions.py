from src.shared.domain.exceptions import DomainError


class InsufficientStockError(DomainError):
    error_code = "INSUFFICIENT_STOCK"

    def __init__(self, product_id: int, quantity: int):
        self.data = {"product_id": product_id, "quantity": quantity}
        super().__init__(
            message=f"Insufficient stock for product {product_id} with quantity {quantity}",
            detail=f"product_id={product_id}, quantity={quantity}",
        )
