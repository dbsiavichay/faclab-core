from fastapi import APIRouter, Depends
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
    CategoryQueryParams,
    CategoryRequest,
    CategoryResponse,
    ProductQueryParams,
    ProductRequest,
    ProductResponse,
)
from src.shared.infra.dependencies import get_meta
from src.shared.infra.validators import (
    RESPONSES_COMMAND,
    RESPONSES_DELETE,
    RESPONSES_LIST,
    RESPONSES_QUERY,
    DataResponse,
    Meta,
    PaginatedDataResponse,
)


class CategoryRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Sets up all the routes for the router."""
        self.router.post(
            "",
            response_model=DataResponse[CategoryResponse],
            summary="Save category",
            responses=RESPONSES_COMMAND,
        )(self.create)
        self.router.put(
            "/{id}",
            response_model=DataResponse[CategoryResponse],
            summary="Update category",
            responses=RESPONSES_COMMAND,
        )(self.update)
        self.router.delete(
            "/{id}", summary="Delete category", responses=RESPONSES_DELETE
        )(self.delete)
        self.router.get(
            "",
            response_model=PaginatedDataResponse[CategoryResponse],
            summary="Get all categories",
            responses=RESPONSES_LIST,
        )(self.get_all)
        self.router.get(
            "/{id}",
            response_model=DataResponse[CategoryResponse],
            summary="Get category by ID",
            responses=RESPONSES_QUERY,
        )(self.get_by_id)

    def create(
        self,
        new_category: CategoryRequest,
        handler: Injected[CreateCategoryCommandHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[CategoryResponse]:
        """Saves a category."""
        result = handler.handle(
            CreateCategoryCommand(**new_category.model_dump(exclude_none=True))
        )
        return DataResponse(data=CategoryResponse.model_validate(result), meta=meta)

    def update(
        self,
        id: int,
        category: CategoryRequest,
        handler: Injected[UpdateCategoryCommandHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[CategoryResponse]:
        """Updates a category."""
        result = handler.handle(
            UpdateCategoryCommand(
                category_id=id, **category.model_dump(exclude_none=True)
            )
        )
        return DataResponse(data=CategoryResponse.model_validate(result), meta=meta)

    def delete(self, id: int, handler: Injected[DeleteCategoryCommandHandler]) -> None:
        """Deletes a category."""
        handler.handle(DeleteCategoryCommand(category_id=id))

    def get_all(
        self,
        handler: Injected[GetAllCategoriesQueryHandler],
        query_params: CategoryQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> PaginatedDataResponse[CategoryResponse]:
        """Retrieves all categories."""
        result = handler.handle(
            GetAllCategoriesQuery(**query_params.model_dump(exclude_none=True))
        )
        return PaginatedDataResponse(
            data=[CategoryResponse.model_validate(c) for c in result["items"]],
            meta=meta.with_pagination(
                total=result["total"],
                limit=result["limit"],
                offset=result["offset"],
            ),
        )

    def get_by_id(
        self,
        id: int,
        handler: Injected[GetCategoryByIdQueryHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[CategoryResponse]:
        """Retrieves a specific category by its ID."""
        result = handler.handle(GetCategoryByIdQuery(category_id=id))
        return DataResponse(data=CategoryResponse.model_validate(result), meta=meta)


class ProductRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Sets up all the routes for the router."""
        self.router.post(
            "",
            response_model=DataResponse[ProductResponse],
            summary="Save product",
            responses=RESPONSES_COMMAND,
        )(self.create)
        self.router.put(
            "/{id}",
            response_model=DataResponse[ProductResponse],
            summary="Update product",
            responses=RESPONSES_COMMAND,
        )(self.update)
        self.router.delete(
            "/{id}", summary="Delete product", responses=RESPONSES_DELETE
        )(self.delete)
        self.router.get(
            "",
            response_model=PaginatedDataResponse[ProductResponse],
            summary="Get all products",
            responses=RESPONSES_LIST,
        )(self.get_all)
        self.router.get(
            "/{id}",
            response_model=DataResponse[ProductResponse],
            summary="Get product by ID",
            responses=RESPONSES_QUERY,
        )(self.get_by_id)

    def create(
        self,
        new_product: ProductRequest,
        handler: Injected[CreateProductCommandHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[ProductResponse]:
        """Saves a product."""
        result = handler.handle(
            CreateProductCommand(**new_product.model_dump(exclude_none=True))
        )
        return DataResponse(data=ProductResponse.model_validate(result), meta=meta)

    def update(
        self,
        id: int,
        product: ProductRequest,
        handler: Injected[UpdateProductCommandHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[ProductResponse]:
        """Updates a product."""
        result = handler.handle(
            UpdateProductCommand(product_id=id, **product.model_dump(exclude_none=True))
        )
        return DataResponse(data=ProductResponse.model_validate(result), meta=meta)

    def delete(self, id: int, handler: Injected[DeleteProductCommandHandler]) -> None:
        """Deletes a product."""
        handler.handle(DeleteProductCommand(product_id=id))

    def get_all(
        self,
        handler: Injected[GetAllProductsQueryHandler],
        query_params: ProductQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> PaginatedDataResponse[ProductResponse]:
        """Retrieves all products."""
        result = handler.handle(
            GetAllProductsQuery(**query_params.model_dump(exclude_none=True))
        )
        return PaginatedDataResponse(
            data=[ProductResponse.model_validate(p) for p in result["items"]],
            meta=meta.with_pagination(
                total=result["total"],
                limit=result["limit"],
                offset=result["offset"],
            ),
        )

    def get_by_id(
        self,
        id: int,
        handler: Injected[GetProductByIdQueryHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[ProductResponse]:
        """Retrieves a specific product by its ID."""
        result = handler.handle(GetProductByIdQuery(product_id=id))
        return DataResponse(data=ProductResponse.model_validate(result), meta=meta)
