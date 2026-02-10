from dataclasses import dataclass
from typing import List

from src.sales.domain.entities import SaleItem
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetSaleItemsQuery(Query):
    """Query para obtener los items de una venta"""

    sale_id: int


class GetSaleItemsQueryHandler(QueryHandler[GetSaleItemsQuery, List[dict]]):
    """Handler para obtener todos los items de una venta"""

    def __init__(self, repo: Repository[SaleItem]):
        self.repo = repo

    def handle(self, query: GetSaleItemsQuery) -> List[dict]:
        """Obtiene todos los items de una venta específica"""
        items = self.repo.filter_by(sale_id=query.sale_id)
        return [item.dict() for item in items]
