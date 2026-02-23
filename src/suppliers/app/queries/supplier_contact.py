from dataclasses import dataclass

from wireup import injectable

from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError
from src.suppliers.domain.entities import SupplierContact


@dataclass
class GetSupplierContactByIdQuery(Query):
    id: int = 0


@injectable(lifetime="scoped")
class GetSupplierContactByIdQueryHandler(
    QueryHandler[GetSupplierContactByIdQuery, dict]
):
    def __init__(self, repo: Repository[SupplierContact]):
        self.repo = repo

    def _handle(self, query: GetSupplierContactByIdQuery) -> dict:
        contact = self.repo.get_by_id(query.id)
        if contact is None:
            raise NotFoundError(f"Supplier contact with id {query.id} not found")
        return contact.dict()


@dataclass
class GetContactsBySupplierIdQuery(Query):
    supplier_id: int = 0


@injectable(lifetime="scoped")
class GetContactsBySupplierIdQueryHandler(
    QueryHandler[GetContactsBySupplierIdQuery, list[dict]]
):
    def __init__(self, repo: Repository[SupplierContact]):
        self.repo = repo

    def _handle(self, query: GetContactsBySupplierIdQuery) -> list[dict]:
        contacts = self.repo.filter_by(supplier_id=query.supplier_id)
        return [contact.dict() for contact in contacts]
