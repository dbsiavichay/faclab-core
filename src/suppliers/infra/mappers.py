from wireup import injectable

from src.shared.infra.mappers import Mapper
from src.suppliers.domain.entities import Supplier, SupplierContact, SupplierProduct
from src.suppliers.infra.models import (
    SupplierContactModel,
    SupplierModel,
    SupplierProductModel,
)


@injectable(lifetime="singleton")
class SupplierMapper(Mapper[Supplier, SupplierModel]):
    __entity__ = Supplier
    __exclude_fields__ = frozenset({"created_at"})


@injectable(lifetime="singleton")
class SupplierContactMapper(Mapper[SupplierContact, SupplierContactModel]):
    __entity__ = SupplierContact


@injectable(lifetime="singleton")
class SupplierProductMapper(Mapper[SupplierProduct, SupplierProductModel]):
    __entity__ = SupplierProduct
