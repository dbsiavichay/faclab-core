from src.shared.app.repositories import Repository
from src.suppliers.domain.entities import Supplier, SupplierContact, SupplierProduct


class SupplierRepository(Repository[Supplier]):
    pass


class SupplierContactRepository(Repository[SupplierContact]):
    pass


class SupplierProductRepository(Repository[SupplierProduct]):
    pass
