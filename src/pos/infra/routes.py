"""POS read-only routes for products and customers"""

from fastapi import APIRouter, Query
from wireup import Injected

from src.catalog.product.app.queries.get_products import (
    GetAllProductsQuery,
    GetAllProductsQueryHandler,
    GetProductByIdQuery,
    GetProductByIdQueryHandler,
)
from src.catalog.product.infra.validators import ProductResponse
from src.customers.app.queries.customer import (
    GetAllCustomersQuery,
    GetAllCustomersQueryHandler,
    GetCustomerByIdQuery,
    GetCustomerByIdQueryHandler,
    GetCustomerByTaxIdQuery,
    GetCustomerByTaxIdQueryHandler,
)
from src.customers.infra.validators import CustomerResponse


class POSProductRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get(
            "", response_model=list[ProductResponse], summary="List products"
        )(self.get_all)
        self.router.get("/{id}", response_model=ProductResponse, summary="Get product")(
            self.get_by_id
        )

    def get_all(
        self, handler: Injected[GetAllProductsQueryHandler]
    ) -> list[ProductResponse]:
        result = handler.handle(GetAllProductsQuery())
        return [ProductResponse.model_validate(p) for p in result]

    def get_by_id(
        self, id: int, handler: Injected[GetProductByIdQueryHandler]
    ) -> ProductResponse:
        result = handler.handle(GetProductByIdQuery(product_id=id))
        return ProductResponse.model_validate(result)


class POSCustomerRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get(
            "", response_model=list[CustomerResponse], summary="List customers"
        )(self.get_all)
        self.router.get(
            "/search/by-tax-id",
            response_model=CustomerResponse,
            summary="Search customer by tax ID",
        )(self.get_by_tax_id)
        self.router.get(
            "/{id}", response_model=CustomerResponse, summary="Get customer"
        )(self.get_by_id)

    def get_all(
        self, handler: Injected[GetAllCustomersQueryHandler]
    ) -> list[CustomerResponse]:
        result = handler.handle(GetAllCustomersQuery())
        return [CustomerResponse.model_validate(c) for c in result]

    def get_by_id(
        self, id: int, handler: Injected[GetCustomerByIdQueryHandler]
    ) -> CustomerResponse:
        result = handler.handle(GetCustomerByIdQuery(id=id))
        return CustomerResponse.model_validate(result)

    def get_by_tax_id(
        self,
        handler: Injected[GetCustomerByTaxIdQueryHandler],
        tax_id: str = Query(..., description="Tax ID to search for"),
    ) -> CustomerResponse:
        result = handler.handle(GetCustomerByTaxIdQuery(tax_id=tax_id))
        return CustomerResponse.model_validate(result)
