"""POS read-only routes for products and customers"""

from fastapi import APIRouter, Query
from wireup import Injected

from src.catalog.product.infra.controllers import ProductController
from src.catalog.product.infra.validators import ProductResponse
from src.customers.infra.controllers import CustomerController
from src.customers.infra.validators import CustomerResponse


class POSProductRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get("", response_model=list[ProductResponse])(self.get_all)
        self.router.get("/{id}", response_model=ProductResponse)(self.get_by_id)

    def get_all(self, controller: Injected[ProductController]):
        return controller.get_all()

    def get_by_id(self, id: int, controller: Injected[ProductController]):
        return controller.get_by_id(id)


class POSCustomerRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get("", response_model=list[CustomerResponse])(self.get_all)
        self.router.get(
            "/search/by-tax-id",
            response_model=CustomerResponse,
        )(self.get_by_tax_id)
        self.router.get("/{id}", response_model=CustomerResponse)(self.get_by_id)

    def get_all(self, controller: Injected[CustomerController]):
        return controller.get_all()

    def get_by_id(self, id: int, controller: Injected[CustomerController]):
        return controller.get_by_id(id)

    def get_by_tax_id(
        self,
        controller: Injected[CustomerController],
        tax_id: str = Query(..., description="Tax ID to search for"),
    ):
        return controller.get_by_tax_id(tax_id)
