from dataclasses import dataclass

from wireup import injectable

from src.customers.app.types import CustomerContactOutput
from src.customers.domain.entities import CustomerContact
from src.customers.infra.repositories import CustomerContactRepositoryImpl
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetCustomerContactByIdQuery(Query):
    id: int = 0


@injectable(lifetime="scoped")
class GetCustomerContactByIdQueryHandler(
    QueryHandler[GetCustomerContactByIdQuery, CustomerContactOutput | None]
):
    def __init__(self, repo: Repository[CustomerContact]):
        self.repo = repo

    def _handle(
        self, query: GetCustomerContactByIdQuery
    ) -> CustomerContactOutput | None:
        contact = self.repo.get_by_id(query.id)
        if contact is None:
            return None
        return contact.dict()


@dataclass
class GetContactsByCustomerIdQuery(Query):
    customer_id: int = 0


@injectable(lifetime="scoped")
class GetContactsByCustomerIdQueryHandler(
    QueryHandler[GetContactsByCustomerIdQuery, list[CustomerContactOutput]]
):
    def __init__(self, repo: Repository[CustomerContact]):
        self.repo = repo

    def _handle(
        self, query: GetContactsByCustomerIdQuery
    ) -> list[CustomerContactOutput]:
        if isinstance(self.repo, CustomerContactRepositoryImpl):
            contacts = self.repo.get_by_customer_id(query.customer_id)
            return [contact.dict() for contact in contacts]
        return []
