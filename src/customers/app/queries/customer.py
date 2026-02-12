from dataclasses import dataclass

from src.customers.app.types import CustomerOutput
from src.customers.domain.entities import Customer
from src.customers.infra.repositories import CustomerRepositoryImpl
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetAllCustomersQuery(Query):
    pass


class GetAllCustomersQueryHandler(
    QueryHandler[GetAllCustomersQuery, list[CustomerOutput]]
):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def handle(self, query: GetAllCustomersQuery) -> list[CustomerOutput]:
        customers = self.repo.get_all()
        return [customer.dict() for customer in customers]


@dataclass
class GetCustomerByIdQuery(Query):
    id: int = 0


class GetCustomerByIdQueryHandler(
    QueryHandler[GetCustomerByIdQuery, CustomerOutput | None]
):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def handle(self, query: GetCustomerByIdQuery) -> CustomerOutput | None:
        customer = self.repo.get_by_id(query.id)
        if customer is None:
            return None
        return customer.dict()


@dataclass
class GetCustomerByTaxIdQuery(Query):
    tax_id: str = ""


class GetCustomerByTaxIdQueryHandler(
    QueryHandler[GetCustomerByTaxIdQuery, CustomerOutput | None]
):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def handle(self, query: GetCustomerByTaxIdQuery) -> CustomerOutput | None:
        if isinstance(self.repo, CustomerRepositoryImpl):
            customer = self.repo.get_by_tax_id(query.tax_id)
            if customer is None:
                return None
            return customer.dict()
        return None
