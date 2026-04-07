from src.sales.domain.entities import Payment, Sale, SaleItem
from src.shared.app.repositories import Repository


class SaleRepository(Repository[Sale]):
    pass


class SaleItemRepository(Repository[SaleItem]):
    pass


class PaymentRepository(Repository[Payment]):
    pass
