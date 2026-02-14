from dataclasses import dataclass

from wireup import injectable

from src.customers.domain.entities import Customer
from src.customers.infra.repositories import CustomerRepositoryImpl
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetAllCustomersQuery(Query):
    pass


@injectable(lifetime="scoped")
class GetAllCustomersQueryHandler(QueryHandler[GetAllCustomersQuery, list[dict]]):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def _handle(self, query: GetAllCustomersQuery) -> list[dict]:
        customers = self.repo.get_all()
        return [customer.dict() for customer in customers]


@dataclass
class GetCustomerByIdQuery(Query):
    id: int = 0


@injectable(lifetime="scoped")
class GetCustomerByIdQueryHandler(QueryHandler[GetCustomerByIdQuery, dict | None]):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def _handle(self, query: GetCustomerByIdQuery) -> dict | None:
        customer = self.repo.get_by_id(query.id)
        if customer is None:
            return None
        return customer.dict()


@dataclass
class GetCustomerByTaxIdQuery(Query):
    tax_id: str = ""


@injectable(lifetime="scoped")
class GetCustomerByTaxIdQueryHandler(
    QueryHandler[GetCustomerByTaxIdQuery, dict | None]
):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def _handle(self, query: GetCustomerByTaxIdQuery) -> dict | None:
        if isinstance(self.repo, CustomerRepositoryImpl):
            customer = self.repo.get_by_tax_id(query.tax_id)
            if customer is None:
                return None
            return customer.dict()
        return None
