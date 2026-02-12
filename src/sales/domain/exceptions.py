"""Excepciones específicas del dominio de Sales"""


class SalesError(Exception):
    """Excepción base para el dominio de sales"""

    pass


class InvalidSaleStatusError(SalesError):
    """Se lanza cuando se intenta realizar una operación con un estado inválido"""

    def __init__(self, current_status: str, operation: str):
        self.current_status = current_status
        self.operation = operation
        super().__init__(f"Cannot {operation} sale with status {current_status}")


class SaleHasNoItemsError(SalesError):
    """Se lanza cuando se intenta confirmar una venta sin items"""

    def __init__(self, sale_id: int):
        self.sale_id = sale_id
        super().__init__(f"Sale {sale_id} has no items")


class InsufficientStockError(SalesError):
    """Se lanza cuando no hay suficiente stock para confirmar una venta"""

    def __init__(self, product_id: int, requested: int, available: int):
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for product {product_id}. "
            f"Requested: {requested}, Available: {available}"
        )
