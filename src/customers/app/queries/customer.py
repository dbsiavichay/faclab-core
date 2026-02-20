from dataclasses import dataclass

from wireup import injectable

from src.customers.domain.entities import Customer
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


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
class GetCustomerByIdQueryHandler(QueryHandler[GetCustomerByIdQuery, dict]):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def _handle(self, query: GetCustomerByIdQuery) -> dict:
        customer = self.repo.get_by_id(query.id)
        if customer is None:
            raise NotFoundError(f"Customer with id {query.id} not found")
        return customer.dict()


@dataclass
class GetCustomerByTaxIdQuery(Query):
    tax_id: str = ""


@injectable(lifetime="scoped")
class GetCustomerByTaxIdQueryHandler(QueryHandler[GetCustomerByTaxIdQuery, dict]):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def _handle(self, query: GetCustomerByTaxIdQuery) -> dict:
        customer = self.repo.first(tax_id=query.tax_id)
        if customer is None:
            raise NotFoundError(f"Customer with tax_id {query.tax_id} not found")
        return customer.dict()
