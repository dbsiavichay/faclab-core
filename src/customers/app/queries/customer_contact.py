from dataclasses import dataclass

from wireup import injectable

from src.customers.domain.entities import CustomerContact
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class GetCustomerContactByIdQuery(Query):
    id: int = 0


@injectable(lifetime="scoped")
class GetCustomerContactByIdQueryHandler(
    QueryHandler[GetCustomerContactByIdQuery, dict]
):
    def __init__(self, repo: Repository[CustomerContact]):
        self.repo = repo

    def _handle(self, query: GetCustomerContactByIdQuery) -> dict:
        contact = self.repo.get_by_id(query.id)
        if contact is None:
            raise NotFoundError(f"Customer contact with id {query.id} not found")
        return contact.dict()


@dataclass
class GetContactsByCustomerIdQuery(Query):
    customer_id: int = 0


@injectable(lifetime="scoped")
class GetContactsByCustomerIdQueryHandler(
    QueryHandler[GetContactsByCustomerIdQuery, list[dict]]
):
    def __init__(self, repo: Repository[CustomerContact]):
        self.repo = repo

    def _handle(self, query: GetContactsByCustomerIdQuery) -> list[dict]:
        contacts = self.repo.filter_by(customer_id=query.customer_id)
        return [contact.dict() for contact in contacts]
