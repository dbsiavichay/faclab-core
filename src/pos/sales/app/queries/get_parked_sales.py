from dataclasses import dataclass

from wireup import injectable

from src.sales.app.repositories import SaleRepository
from src.sales.domain.specifications import ParkedSalesSpecification
from src.shared.app.queries import Query, QueryHandler


@dataclass
class GetParkedSalesQuery(Query):
    """Query para obtener ventas aparcadas"""


@injectable(lifetime="scoped")
class GetParkedSalesQueryHandler(QueryHandler[GetParkedSalesQuery, list[dict]]):
    def __init__(self, repo: SaleRepository):
        self.repo = repo

    def _handle(self, query: GetParkedSalesQuery) -> list[dict]:
        spec = ParkedSalesSpecification()
        sales = self.repo.filter_by_spec(spec)
        return [sale.dict() for sale in sales]
