from fastapi import APIRouter
from wireup import Injected

from src.catalog.product.infra.controllers import CategoryController, ProductController
from src.catalog.product.infra.validators import (
    CategoryRequest,
    CategoryResponse,
    ProductRequest,
    ProductResponse,
    ProductsResponse,
)


class CategoryRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Sets up all the routes for the router."""
        self.router.post("", response_model=CategoryResponse, summary="Save category")(
            self.create
        )
        self.router.put(
            "/{id}", response_model=CategoryResponse, summary="Update category"
        )(self.update)
        self.router.delete("/{id}", summary="Delete category")(self.delete)
        self.router.get(
            "", response_model=list[CategoryResponse], summary="Get all categories"
        )(self.get_all)
        self.router.get(
            "/{id}", response_model=CategoryResponse, summary="Get category by ID"
        )(self.get_by_id)

    def create(
        self,
        new_category: CategoryRequest,
        controller: Injected[CategoryController],
    ):
        """Saves a category."""
        return controller.create(new_category)

    def update(
        self,
        id: int,
        category: CategoryRequest,
        controller: Injected[CategoryController],
    ):
        """Updates a category."""
        return controller.update(id, category)

    def delete(self, id: int, controller: Injected[CategoryController]):
        """Deletes a category."""
        return controller.delete(id)

    def get_all(self, controller: Injected[CategoryController]):
        """Retrieves all categories."""
        return controller.get_all()

    def get_by_id(self, id: int, controller: Injected[CategoryController]):
        """Retrieves a specific category by its ID."""
        return controller.get_by_id(id)


class ProductRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Sets up all the routes for the router."""
        self.router.post("", response_model=ProductResponse, summary="Save product")(
            self.create
        )
        self.router.put(
            "/{id}", response_model=ProductResponse, summary="Update product"
        )(self.update)
        self.router.delete("/{id}", summary="Delete product")(self.delete)
        self.router.get(
            "", response_model=ProductsResponse, summary="Get all products"
        )(self.get_all)
        self.router.get(
            "/{id}", response_model=ProductResponse, summary="Get product by ID"
        )(self.get_by_id)

    def create(
        self,
        new_product: ProductRequest,
        controller: Injected[ProductController],
    ):
        """Saves a product."""
        return controller.create(new_product)

    def update(
        self,
        id: int,
        product: ProductRequest,
        controller: Injected[ProductController],
    ):
        """Updates a product."""
        return controller.update(id, product)

    def delete(self, id: int, controller: Injected[ProductController]):
        """Deletes a product."""
        return controller.delete(id)

    def get_all(self, controller: Injected[ProductController]):
        """Retrieves all products."""
        return controller.get_all()

    def get_by_id(self, id: int, controller: Injected[ProductController]):
        """Retrieves a specific product by its ID."""
        return controller.get_by_id(id)
