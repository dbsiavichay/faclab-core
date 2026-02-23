from fastapi import APIRouter, Query
from wireup import Injected

from src.suppliers.app.commands.supplier import (
    ActivateSupplierCommand,
    ActivateSupplierCommandHandler,
    CreateSupplierCommand,
    CreateSupplierCommandHandler,
    DeactivateSupplierCommand,
    DeactivateSupplierCommandHandler,
    DeleteSupplierCommand,
    DeleteSupplierCommandHandler,
    UpdateSupplierCommand,
    UpdateSupplierCommandHandler,
)
from src.suppliers.app.commands.supplier_contact import (
    CreateSupplierContactCommand,
    CreateSupplierContactCommandHandler,
    DeleteSupplierContactCommand,
    DeleteSupplierContactCommandHandler,
    UpdateSupplierContactCommand,
    UpdateSupplierContactCommandHandler,
)
from src.suppliers.app.commands.supplier_product import (
    CreateSupplierProductCommand,
    CreateSupplierProductCommandHandler,
    DeleteSupplierProductCommand,
    DeleteSupplierProductCommandHandler,
    UpdateSupplierProductCommand,
    UpdateSupplierProductCommandHandler,
)
from src.suppliers.app.queries.supplier import (
    GetAllSuppliersQuery,
    GetAllSuppliersQueryHandler,
    GetSupplierByIdQuery,
    GetSupplierByIdQueryHandler,
)
from src.suppliers.app.queries.supplier_contact import (
    GetContactsBySupplierIdQuery,
    GetContactsBySupplierIdQueryHandler,
    GetSupplierContactByIdQuery,
    GetSupplierContactByIdQueryHandler,
)
from src.suppliers.app.queries.supplier_product import (
    GetProductSuppliersByProductIdQuery,
    GetProductSuppliersByProductIdQueryHandler,
    GetSupplierProductByIdQuery,
    GetSupplierProductByIdQueryHandler,
    GetSupplierProductsBySupplierIdQuery,
    GetSupplierProductsBySupplierIdQueryHandler,
)
from src.suppliers.infra.validators import (
    SupplierContactRequest,
    SupplierContactResponse,
    SupplierProductRequest,
    SupplierProductResponse,
    SupplierRequest,
    SupplierResponse,
)


class SupplierRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Sets up all the routes for the router."""
        self.router.post(
            "", response_model=SupplierResponse, summary="Create supplier"
        )(self.create)
        self.router.put(
            "/{id}", response_model=SupplierResponse, summary="Update supplier"
        )(self.update)
        self.router.delete("/{id}", summary="Delete supplier")(self.delete)
        self.router.get(
            "", response_model=list[SupplierResponse], summary="Get all suppliers"
        )(self.get_all)
        self.router.get(
            "/{id}", response_model=SupplierResponse, summary="Get supplier by ID"
        )(self.get_by_id)
        self.router.post(
            "/{id}/activate",
            response_model=SupplierResponse,
            summary="Activate supplier",
        )(self.activate)
        self.router.post(
            "/{id}/deactivate",
            response_model=SupplierResponse,
            summary="Deactivate supplier",
        )(self.deactivate)
        self.router.post(
            "/{supplier_id}/contacts",
            response_model=SupplierContactResponse,
            summary="Create supplier contact",
        )(self.create_contact)
        self.router.get(
            "/{supplier_id}/contacts",
            response_model=list[SupplierContactResponse],
            summary="Get supplier contacts",
        )(self.get_supplier_contacts)
        self.router.post(
            "/{supplier_id}/products",
            response_model=SupplierProductResponse,
            summary="Add product to supplier catalog",
        )(self.create_supplier_product)
        self.router.get(
            "/{supplier_id}/products",
            response_model=list[SupplierProductResponse],
            summary="Get supplier products",
        )(self.get_supplier_products)

    def create(
        self,
        handler: Injected[CreateSupplierCommandHandler],
        new_supplier: SupplierRequest,
    ) -> SupplierResponse:
        """Creates a new supplier."""
        result = handler.handle(
            CreateSupplierCommand(**new_supplier.model_dump(exclude_none=True))
        )
        return SupplierResponse.model_validate(result)

    def update(
        self,
        handler: Injected[UpdateSupplierCommandHandler],
        id: int,
        supplier: SupplierRequest,
    ) -> SupplierResponse:
        """Updates a supplier."""
        result = handler.handle(
            UpdateSupplierCommand(id=id, **supplier.model_dump(exclude_none=True))
        )
        return SupplierResponse.model_validate(result)

    def delete(
        self,
        handler: Injected[DeleteSupplierCommandHandler],
        id: int,
    ) -> None:
        """Deletes a supplier."""
        handler.handle(DeleteSupplierCommand(id=id))

    def get_all(
        self,
        handler: Injected[GetAllSuppliersQueryHandler],
        is_active: bool | None = Query(None, description="Filter by active status"),
    ) -> list[SupplierResponse]:
        """Retrieves all suppliers."""
        result = handler.handle(GetAllSuppliersQuery(is_active=is_active))
        return [SupplierResponse.model_validate(s) for s in result]

    def get_by_id(
        self, handler: Injected[GetSupplierByIdQueryHandler], id: int
    ) -> SupplierResponse:
        """Retrieves a specific supplier by its ID."""
        result = handler.handle(GetSupplierByIdQuery(id=id))
        return SupplierResponse.model_validate(result)

    def activate(
        self, handler: Injected[ActivateSupplierCommandHandler], id: int
    ) -> SupplierResponse:
        """Activates a supplier."""
        result = handler.handle(ActivateSupplierCommand(id=id))
        return SupplierResponse.model_validate(result)

    def deactivate(
        self, handler: Injected[DeactivateSupplierCommandHandler], id: int
    ) -> SupplierResponse:
        """Deactivates a supplier."""
        result = handler.handle(DeactivateSupplierCommand(id=id))
        return SupplierResponse.model_validate(result)

    def create_contact(
        self,
        handler: Injected[CreateSupplierContactCommandHandler],
        supplier_id: int,
        new_contact: SupplierContactRequest,
    ) -> SupplierContactResponse:
        """Creates a new contact for a supplier."""
        result = handler.handle(
            CreateSupplierContactCommand(
                supplier_id=supplier_id, **new_contact.model_dump(exclude_none=True)
            )
        )
        return SupplierContactResponse.model_validate(result)

    def get_supplier_contacts(
        self,
        handler: Injected[GetContactsBySupplierIdQueryHandler],
        supplier_id: int,
    ) -> list[SupplierContactResponse]:
        """Retrieves all contacts for a supplier."""
        result = handler.handle(GetContactsBySupplierIdQuery(supplier_id=supplier_id))
        return [SupplierContactResponse.model_validate(c) for c in result]

    def create_supplier_product(
        self,
        handler: Injected[CreateSupplierProductCommandHandler],
        supplier_id: int,
        new_product: SupplierProductRequest,
    ) -> SupplierProductResponse:
        """Adds a product to the supplier catalog."""
        result = handler.handle(
            CreateSupplierProductCommand(
                supplier_id=supplier_id,
                **new_product.model_dump(exclude_none=True, exclude={"supplier_id"}),
            )
        )
        return SupplierProductResponse.model_validate(result)

    def get_supplier_products(
        self,
        handler: Injected[GetSupplierProductsBySupplierIdQueryHandler],
        supplier_id: int,
    ) -> list[SupplierProductResponse]:
        """Retrieves all products for a supplier."""
        result = handler.handle(
            GetSupplierProductsBySupplierIdQuery(supplier_id=supplier_id)
        )
        return [SupplierProductResponse.model_validate(p) for p in result]


class SupplierContactRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Sets up all the routes for the router."""
        self.router.put(
            "/{id}",
            response_model=SupplierContactResponse,
            summary="Update supplier contact",
        )(self.update)
        self.router.delete("/{id}", summary="Delete supplier contact")(self.delete)
        self.router.get(
            "/{id}",
            response_model=SupplierContactResponse,
            summary="Get supplier contact by ID",
        )(self.get_by_id)

    def update(
        self,
        handler: Injected[UpdateSupplierContactCommandHandler],
        id: int,
        contact: SupplierContactRequest,
    ) -> SupplierContactResponse:
        """Updates a supplier contact."""
        result = handler.handle(
            UpdateSupplierContactCommand(id=id, **contact.model_dump(exclude_none=True))
        )
        return SupplierContactResponse.model_validate(result)

    def delete(
        self,
        handler: Injected[DeleteSupplierContactCommandHandler],
        id: int,
    ) -> None:
        """Deletes a supplier contact."""
        handler.handle(DeleteSupplierContactCommand(id=id))

    def get_by_id(
        self,
        handler: Injected[GetSupplierContactByIdQueryHandler],
        id: int,
    ) -> SupplierContactResponse:
        """Retrieves a specific supplier contact by its ID."""
        result = handler.handle(GetSupplierContactByIdQuery(id=id))
        return SupplierContactResponse.model_validate(result)


class SupplierProductRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Sets up all the routes for the router."""
        self.router.put(
            "/{id}",
            response_model=SupplierProductResponse,
            summary="Update supplier product",
        )(self.update)
        self.router.delete("/{id}", summary="Delete supplier product")(self.delete)
        self.router.get(
            "/{id}",
            response_model=SupplierProductResponse,
            summary="Get supplier product by ID",
        )(self.get_by_id)
        self.router.get(
            "/by-product/{product_id}",
            response_model=list[SupplierProductResponse],
            summary="Get all suppliers for a product",
        )(self.get_by_product)

    def update(
        self,
        handler: Injected[UpdateSupplierProductCommandHandler],
        id: int,
        product: SupplierProductRequest,
    ) -> SupplierProductResponse:
        """Updates a supplier product."""
        result = handler.handle(
            UpdateSupplierProductCommand(id=id, **product.model_dump(exclude_none=True))
        )
        return SupplierProductResponse.model_validate(result)

    def delete(
        self,
        handler: Injected[DeleteSupplierProductCommandHandler],
        id: int,
    ) -> None:
        """Deletes a supplier product."""
        handler.handle(DeleteSupplierProductCommand(id=id))

    def get_by_id(
        self,
        handler: Injected[GetSupplierProductByIdQueryHandler],
        id: int,
    ) -> SupplierProductResponse:
        """Retrieves a specific supplier product by its ID."""
        result = handler.handle(GetSupplierProductByIdQuery(id=id))
        return SupplierProductResponse.model_validate(result)

    def get_by_product(
        self,
        handler: Injected[GetProductSuppliersByProductIdQueryHandler],
        product_id: int,
    ) -> list[SupplierProductResponse]:
        """Retrieves all supplier entries for a given product."""
        result = handler.handle(
            GetProductSuppliersByProductIdQuery(product_id=product_id)
        )
        return [SupplierProductResponse.model_validate(p) for p in result]
