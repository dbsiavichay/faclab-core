from dataclasses import dataclass

from wireup import injectable

from src.sales.app.repositories import SaleItemRepository
from src.shared.app.queries import Query, QueryHandler


@dataclass
class GetSaleItemsQuery(Query):
    """Query para obtener los items de una venta"""

    sale_id: int


@injectable(lifetime="scoped")
class GetSaleItemsQueryHandler(QueryHandler[GetSaleItemsQuery, list[dict]]):
    """Handler para obtener todos los items de una venta"""

    def __init__(self, repo: SaleItemRepository):
        self.repo = repo

    def _handle(self, query: GetSaleItemsQuery) -> list[dict]:
        """Obtiene todos los items de una venta específica"""
        items = self.repo.filter_by(sale_id=query.sale_id)
        # Incluir el subtotal calculado en cada item
        result = []
        for item in items:
            item_dict = item.dict()
            item_dict["subtotal"] = item.subtotal
            result.append(item_dict)
        return result
