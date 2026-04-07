from src.pos.refund.domain.entities import Refund, RefundItem, RefundPayment
from src.shared.app.repositories import Repository


class RefundRepository(Repository[Refund]):
    pass


class RefundItemRepository(Repository[RefundItem]):
    pass


class RefundPaymentRepository(Repository[RefundPayment]):
    pass
