"""POS read-only routes for products and customers"""

from fastapi import APIRouter, Depends, Query
from wireup import Injected

from src.catalog.product.app.queries.get_products import (
    GetAllProductsQuery,
    GetAllProductsQueryHandler,
    GetProductByIdQuery,
    GetProductByIdQueryHandler,
    SearchProductsQuery,
    SearchProductsQueryHandler,
)
from src.catalog.product.infra.validators import ProductResponse
from src.customers.app.commands.customer import (
    CreateCustomerCommand,
    CreateCustomerCommandHandler,
)
from src.customers.app.queries.customer import (
    GetAllCustomersQuery,
    GetAllCustomersQueryHandler,
    GetCustomerByIdQuery,
    GetCustomerByIdQueryHandler,
    GetCustomerByTaxIdQuery,
    GetCustomerByTaxIdQueryHandler,
)
from src.customers.infra.validators import CustomerResponse
from src.pos.infra.validators import QuickCustomerRequest
from src.shared.infra.dependencies import get_meta
from src.shared.infra.validators import DataResponse, ListResponse, Meta


class POSProductRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get(
            "",
            response_model=ListResponse[ProductResponse],
            summary="List products",
        )(self.get_all)
        self.router.get(
            "/search",
            response_model=ListResponse[ProductResponse],
            summary="Search products by SKU, barcode or name",
        )(self.search)
        self.router.get(
            "/{id}",
            response_model=DataResponse[ProductResponse],
            summary="Get product",
        )(self.get_by_id)

    def get_all(
        self,
        handler: Injected[GetAllProductsQueryHandler],
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[ProductResponse]:
        result = handler.handle(GetAllProductsQuery())
        return ListResponse(
            data=[ProductResponse.model_validate(p) for p in result], meta=meta
        )

    def search(
        self,
        handler: Injected[SearchProductsQueryHandler],
        term: str = Query(..., description="Search term (SKU, barcode or name)"),
        limit: int = Query(20, ge=1, le=100),
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[ProductResponse]:
        result = handler.handle(SearchProductsQuery(search_term=term, limit=limit))
        return ListResponse(
            data=[ProductResponse.model_validate(p) for p in result], meta=meta
        )

    def get_by_id(
        self,
        id: int,
        handler: Injected[GetProductByIdQueryHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[ProductResponse]:
        result = handler.handle(GetProductByIdQuery(product_id=id))
        return DataResponse(data=ProductResponse.model_validate(result), meta=meta)


class POSCustomerRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=DataResponse[CustomerResponse],
            summary="Quick create customer",
            status_code=201,
        )(self.create)
        self.router.get(
            "",
            response_model=ListResponse[CustomerResponse],
            summary="List customers",
        )(self.get_all)
        self.router.get(
            "/search/by-tax-id",
            response_model=DataResponse[CustomerResponse],
            summary="Search customer by tax ID",
        )(self.get_by_tax_id)
        self.router.get(
            "/{id}",
            response_model=DataResponse[CustomerResponse],
            summary="Get customer",
        )(self.get_by_id)

    def create(
        self,
        data: QuickCustomerRequest,
        handler: Injected[CreateCustomerCommandHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[CustomerResponse]:
        command = CreateCustomerCommand(
            name=data.name,
            tax_id=data.tax_id,
            tax_type=data.tax_type,
        )
        result = handler.handle(command)
        return DataResponse(data=CustomerResponse.model_validate(result), meta=meta)

    def get_all(
        self,
        handler: Injected[GetAllCustomersQueryHandler],
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[CustomerResponse]:
        result = handler.handle(GetAllCustomersQuery())
        return ListResponse(
            data=[CustomerResponse.model_validate(c) for c in result], meta=meta
        )

    def get_by_id(
        self,
        id: int,
        handler: Injected[GetCustomerByIdQueryHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[CustomerResponse]:
        result = handler.handle(GetCustomerByIdQuery(id=id))
        return DataResponse(data=CustomerResponse.model_validate(result), meta=meta)

    def get_by_tax_id(
        self,
        handler: Injected[GetCustomerByTaxIdQueryHandler],
        tax_id: str = Query(..., description="Tax ID to search for"),
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[CustomerResponse]:
        result = handler.handle(GetCustomerByTaxIdQuery(tax_id=tax_id))
        return DataResponse(data=CustomerResponse.model_validate(result), meta=meta)
