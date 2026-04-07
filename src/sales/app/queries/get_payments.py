from dataclasses import dataclass

from wireup import injectable

from src.sales.app.repositories import PaymentRepository
from src.shared.app.queries import Query, QueryHandler


@dataclass
class GetSalePaymentsQuery(Query):
    """Query para obtener los pagos de una venta"""

    sale_id: int


@injectable(lifetime="scoped")
class GetSalePaymentsQueryHandler(QueryHandler[GetSalePaymentsQuery, list[dict]]):
    """Handler para obtener todos los pagos de una venta"""

    def __init__(self, repo: PaymentRepository):
        self.repo = repo

    def _handle(self, query: GetSalePaymentsQuery) -> list[dict]:
        """Obtiene todos los pagos de una venta específica"""
        payments = self.repo.filter_by(sale_id=query.sale_id)
        return [payment.dict() for payment in payments]
