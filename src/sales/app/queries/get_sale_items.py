from dataclasses import dataclass

from wireup import injectable

from src.sales.domain.entities import SaleItem
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetSaleItemsQuery(Query):
    """Query para obtener los items de una venta"""

    sale_id: int


@injectable(lifetime="scoped")
class GetSaleItemsQueryHandler(QueryHandler[GetSaleItemsQuery, list[dict]]):
    """Handler para obtener todos los items de una venta"""

    def __init__(self, repo: Repository[SaleItem]):
        self.repo = repo

    def _handle(self, query: GetSaleItemsQuery) -> list[dict]:
        """Obtiene todos los items de una venta específica"""
        items = self.repo.filter_by(sale_id=query.sale_id)
        # Incluir el subtotal calculado en cada item
        result = []
        for item in items:
            item_dict = item.dict()
            item_dict["subtotal"] = float(item.subtotal)
            result.append(item_dict)
        return result
