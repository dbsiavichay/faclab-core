from dataclasses import dataclass
from typing import List, Optional

from src.sales.domain.entities import Sale
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetAllSalesQuery(Query):
    """Query para obtener todas las ventas con filtros opcionales"""

    customer_id: Optional[int] = None
    status: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class GetAllSalesQueryHandler(QueryHandler[GetAllSalesQuery, List[dict]]):
    """Handler para obtener todas las ventas"""

    def __init__(self, repo: Repository[Sale]):
        self.repo = repo

    def handle(self, query: GetAllSalesQuery) -> List[dict]:
        """Obtiene las ventas con los filtros especificados"""
        # Preparar filtros
        filters = {}
        if query.customer_id is not None:
            filters["customer_id"] = query.customer_id
        if query.status is not None:
            filters["status"] = query.status

        # Aplicar filtros
        if filters:
            sales = self.repo.filter_by(
                limit=query.limit,
                offset=query.offset,
                **filters,
            )
        else:
            sales = self.repo.get_all()

        return [sale.dict() for sale in sales]


@dataclass
class GetSaleByIdQuery(Query):
    """Query para obtener una venta por ID"""

    sale_id: int


class GetSaleByIdQueryHandler(QueryHandler[GetSaleByIdQuery, Optional[dict]]):
    """Handler para obtener una venta por ID"""

    def __init__(self, repo: Repository[Sale]):
        self.repo = repo

    def handle(self, query: GetSaleByIdQuery) -> Optional[dict]:
        """Obtiene una venta específica por ID"""
        sale = self.repo.get_by_id(query.sale_id)
        return sale.dict() if sale else None
