from dataclasses import dataclass
from typing import List

from src.sales.domain.entities import Payment
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetSalePaymentsQuery(Query):
    """Query para obtener los pagos de una venta"""

    sale_id: int


class GetSalePaymentsQueryHandler(QueryHandler[GetSalePaymentsQuery, List[dict]]):
    """Handler para obtener todos los pagos de una venta"""

    def __init__(self, repo: Repository[Payment]):
        self.repo = repo

    def handle(self, query: GetSalePaymentsQuery) -> List[dict]:
        """Obtiene todos los pagos de una venta específica"""
        payments = self.repo.filter_by(sale_id=query.sale_id)
        return [payment.dict() for payment in payments]
