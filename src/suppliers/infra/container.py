from src.suppliers.app.commands.supplier import (
    ActivateSupplierCommandHandler,
    CreateSupplierCommandHandler,
    DeactivateSupplierCommandHandler,
    DeleteSupplierCommandHandler,
    UpdateSupplierCommandHandler,
)
from src.suppliers.app.commands.supplier_contact import (
    CreateSupplierContactCommandHandler,
    DeleteSupplierContactCommandHandler,
    UpdateSupplierContactCommandHandler,
)
from src.suppliers.app.commands.supplier_product import (
    CreateSupplierProductCommandHandler,
    DeleteSupplierProductCommandHandler,
    UpdateSupplierProductCommandHandler,
)
from src.suppliers.app.queries.supplier import (
    GetAllSuppliersQueryHandler,
    GetSupplierByIdQueryHandler,
)
from src.suppliers.app.queries.supplier_contact import (
    GetContactsBySupplierIdQueryHandler,
    GetSupplierContactByIdQueryHandler,
)
from src.suppliers.app.queries.supplier_product import (
    GetProductSuppliersByProductIdQueryHandler,
    GetSupplierProductByIdQueryHandler,
    GetSupplierProductsBySupplierIdQueryHandler,
)
from src.suppliers.infra.mappers import (
    SupplierContactMapper,
    SupplierMapper,
    SupplierProductMapper,
)
from src.suppliers.infra.repositories import (
    SupplierContactRepository,
    SupplierProductRepository,
    SupplierRepository,
)

INJECTABLES = [
    SupplierMapper,
    SupplierContactMapper,
    SupplierProductMapper,
    SupplierRepository,
    SupplierContactRepository,
    SupplierProductRepository,
    CreateSupplierCommandHandler,
    UpdateSupplierCommandHandler,
    DeleteSupplierCommandHandler,
    ActivateSupplierCommandHandler,
    DeactivateSupplierCommandHandler,
    GetAllSuppliersQueryHandler,
    GetSupplierByIdQueryHandler,
    CreateSupplierContactCommandHandler,
    UpdateSupplierContactCommandHandler,
    DeleteSupplierContactCommandHandler,
    GetContactsBySupplierIdQueryHandler,
    GetSupplierContactByIdQueryHandler,
    CreateSupplierProductCommandHandler,
    UpdateSupplierProductCommandHandler,
    DeleteSupplierProductCommandHandler,
    GetSupplierProductsBySupplierIdQueryHandler,
    GetProductSuppliersByProductIdQueryHandler,
    GetSupplierProductByIdQueryHandler,
]
