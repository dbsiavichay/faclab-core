from dataclasses import dataclass

from wireup import injectable

from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError
from src.suppliers.domain.entities import SupplierProduct


@dataclass
class GetSupplierProductByIdQuery(Query):
    id: int = 0


@injectable(lifetime="scoped")
class GetSupplierProductByIdQueryHandler(
    QueryHandler[GetSupplierProductByIdQuery, dict]
):
    def __init__(self, repo: Repository[SupplierProduct]):
        self.repo = repo

    def _handle(self, query: GetSupplierProductByIdQuery) -> dict:
        supplier_product = self.repo.get_by_id(query.id)
        if supplier_product is None:
            raise NotFoundError(f"Supplier product with id {query.id} not found")
        return supplier_product.dict()


@dataclass
class GetSupplierProductsBySupplierIdQuery(Query):
    supplier_id: int = 0


@injectable(lifetime="scoped")
class GetSupplierProductsBySupplierIdQueryHandler(
    QueryHandler[GetSupplierProductsBySupplierIdQuery, list[dict]]
):
    def __init__(self, repo: Repository[SupplierProduct]):
        self.repo = repo

    def _handle(self, query: GetSupplierProductsBySupplierIdQuery) -> list[dict]:
        products = self.repo.filter_by(supplier_id=query.supplier_id)
        return [p.dict() for p in products]


@dataclass
class GetProductSuppliersByProductIdQuery(Query):
    product_id: int = 0


@injectable(lifetime="scoped")
class GetProductSuppliersByProductIdQueryHandler(
    QueryHandler[GetProductSuppliersByProductIdQuery, list[dict]]
):
    def __init__(self, repo: Repository[SupplierProduct]):
        self.repo = repo

    def _handle(self, query: GetProductSuppliersByProductIdQuery) -> list[dict]:
        products = self.repo.filter_by(product_id=query.product_id)
        return [p.dict() for p in products]
