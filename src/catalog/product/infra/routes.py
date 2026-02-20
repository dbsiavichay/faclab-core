from fastapi import APIRouter
from wireup import Injected

from src.catalog.product.app.commands.create_category import (
    CreateCategoryCommand,
    CreateCategoryCommandHandler,
)
from src.catalog.product.app.commands.create_product import (
    CreateProductCommand,
    CreateProductCommandHandler,
)
from src.catalog.product.app.commands.delete_category import (
    DeleteCategoryCommand,
    DeleteCategoryCommandHandler,
)
from src.catalog.product.app.commands.delete_product import (
    DeleteProductCommand,
    DeleteProductCommandHandler,
)
from src.catalog.product.app.commands.update_category import (
    UpdateCategoryCommand,
    UpdateCategoryCommandHandler,
)
from src.catalog.product.app.commands.update_product import (
    UpdateProductCommand,
    UpdateProductCommandHandler,
)
from src.catalog.product.app.queries.get_categories import (
    GetAllCategoriesQuery,
    GetAllCategoriesQueryHandler,
    GetCategoryByIdQuery,
    GetCategoryByIdQueryHandler,
)
from src.catalog.product.app.queries.get_products import (
    GetAllProductsQuery,
    GetAllProductsQueryHandler,
    GetProductByIdQuery,
    GetProductByIdQueryHandler,
)
from src.catalog.product.infra.validators import (
    CategoryRequest,
    CategoryResponse,
    ProductRequest,
    ProductResponse,
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
        handler: Injected[CreateCategoryCommandHandler],
    ) -> CategoryResponse:
        """Saves a category."""
        result = handler.handle(
            CreateCategoryCommand(**new_category.model_dump(exclude_none=True))
        )
        return CategoryResponse.model_validate(result)

    def update(
        self,
        id: int,
        category: CategoryRequest,
        handler: Injected[UpdateCategoryCommandHandler],
    ) -> CategoryResponse:
        """Updates a category."""
        result = handler.handle(
            UpdateCategoryCommand(
                category_id=id, **category.model_dump(exclude_none=True)
            )
        )
        return CategoryResponse.model_validate(result)

    def delete(self, id: int, handler: Injected[DeleteCategoryCommandHandler]) -> None:
        """Deletes a category."""
        handler.handle(DeleteCategoryCommand(category_id=id))

    def get_all(
        self, handler: Injected[GetAllCategoriesQueryHandler]
    ) -> list[CategoryResponse]:
        """Retrieves all categories."""
        result = handler.handle(GetAllCategoriesQuery())
        return [CategoryResponse.model_validate(c) for c in result]

    def get_by_id(
        self, id: int, handler: Injected[GetCategoryByIdQueryHandler]
    ) -> CategoryResponse:
        """Retrieves a specific category by its ID."""
        result = handler.handle(GetCategoryByIdQuery(category_id=id))
        return CategoryResponse.model_validate(result)


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
            "", response_model=list[ProductResponse], summary="Get all products"
        )(self.get_all)
        self.router.get(
            "/{id}", response_model=ProductResponse, summary="Get product by ID"
        )(self.get_by_id)

    def create(
        self,
        new_product: ProductRequest,
        handler: Injected[CreateProductCommandHandler],
    ) -> ProductResponse:
        """Saves a product."""
        result = handler.handle(
            CreateProductCommand(**new_product.model_dump(exclude_none=True))
        )
        return ProductResponse.model_validate(result)

    def update(
        self,
        id: int,
        product: ProductRequest,
        handler: Injected[UpdateProductCommandHandler],
    ) -> ProductResponse:
        """Updates a product."""
        result = handler.handle(
            UpdateProductCommand(product_id=id, **product.model_dump(exclude_none=True))
        )
        return ProductResponse.model_validate(result)

    def delete(self, id: int, handler: Injected[DeleteProductCommandHandler]) -> None:
        """Deletes a product."""
        handler.handle(DeleteProductCommand(product_id=id))

    def get_all(
        self, handler: Injected[GetAllProductsQueryHandler]
    ) -> list[ProductResponse]:
        """Retrieves all products."""
        result = handler.handle(GetAllProductsQuery())
        return [ProductResponse.model_validate(p) for p in result]

    def get_by_id(
        self, id: int, handler: Injected[GetProductByIdQueryHandler]
    ) -> ProductResponse:
        """Retrieves a specific product by its ID."""
        result = handler.handle(GetProductByIdQuery(product_id=id))
        return ProductResponse.model_validate(result)
