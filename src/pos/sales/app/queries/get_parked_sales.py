from dataclasses import dataclass

from wireup import injectable

from src.sales.domain.entities import Sale
from src.sales.domain.specifications import ParkedSalesSpecification
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetParkedSalesQuery(Query):
    """Query para obtener ventas aparcadas"""


@injectable(lifetime="scoped")
class GetParkedSalesQueryHandler(QueryHandler[GetParkedSalesQuery, list[dict]]):
    def __init__(self, repo: Repository[Sale]):
        self.repo = repo

    def _handle(self, query: GetParkedSalesQuery) -> list[dict]:
        spec = ParkedSalesSpecification()
        sales = self.repo.filter_by_spec(spec)
        return [sale.dict() for sale in sales]
