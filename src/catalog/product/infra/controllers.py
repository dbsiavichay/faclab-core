from wireup import injectable

from src.catalog.product.app.commands import (
    CreateCategoryCommand,
    CreateCategoryCommandHandler,
    CreateProductCommand,
    CreateProductCommandHandler,
    DeleteCategoryCommand,
    DeleteCategoryCommandHandler,
    DeleteProductCommand,
    DeleteProductCommandHandler,
    UpdateCategoryCommand,
    UpdateCategoryCommandHandler,
    UpdateProductCommand,
    UpdateProductCommandHandler,
)
from src.catalog.product.app.queries import (
    GetAllCategoriesQuery,
    GetAllCategoriesQueryHandler,
    GetAllProductsQuery,
    GetAllProductsQueryHandler,
    GetCategoryByIdQuery,
    GetCategoryByIdQueryHandler,
    GetProductByIdQuery,
    GetProductByIdQueryHandler,
)
from src.catalog.product.domain.entities import Product
from src.catalog.product.infra.validators import (
    CategoryInput,
    CategoryResponse,
    ProductInput,
    ProductResponse,
    ProductsResponse,
)
from src.shared.infra.exceptions import NotFoundError


@injectable(lifetime="scoped")
class CategoryController:
    def __init__(
        self,
        create_handler: CreateCategoryCommandHandler,
        update_handler: UpdateCategoryCommandHandler,
        delete_handler: DeleteCategoryCommandHandler,
        get_all_handler: GetAllCategoriesQueryHandler,
        get_by_id_handler: GetCategoryByIdQueryHandler,
    ):
        self.create_handler = create_handler
        self.update_handler = update_handler
        self.delete_handler = delete_handler
        self.get_all_handler = get_all_handler
        self.get_by_id_handler = get_by_id_handler

    def create(self, new_category: CategoryInput) -> CategoryResponse:
        command = CreateCategoryCommand(**new_category.model_dump(exclude_none=True))
        category = self.create_handler.handle(command)
        return CategoryResponse.model_validate(category)

    def update(self, id: int, category: CategoryInput) -> Product:
        command = UpdateCategoryCommand(
            category_id=id, **category.model_dump(exclude_none=True)
        )
        category = self.update_handler.handle(command)
        return CategoryResponse.model_validate(category)

    def delete(self, id: int) -> None:
        command = DeleteCategoryCommand(category_id=id)
        self.delete_handler.handle(command)

    def get_all(self) -> list[CategoryResponse]:
        query = GetAllCategoriesQuery()
        categories = self.get_all_handler.handle(query)
        return [CategoryResponse.model_validate(category) for category in categories]

    def get_by_id(self, id: int) -> CategoryResponse:
        query = GetCategoryByIdQuery(category_id=id)
        category = self.get_by_id_handler.handle(query)
        if category is None:
            raise NotFoundError("Category not found")
        return CategoryResponse.model_validate(category)


@injectable(lifetime="scoped")
class ProductController:
    def __init__(
        self,
        create_handler: CreateProductCommandHandler,
        update_handler: UpdateProductCommandHandler,
        delete_handler: DeleteProductCommandHandler,
        get_all_handler: GetAllProductsQueryHandler,
        get_by_id_handler: GetProductByIdQueryHandler,
    ):
        self.create_handler = create_handler
        self.update_handler = update_handler
        self.delete_handler = delete_handler
        self.get_all_handler = get_all_handler
        self.get_by_id_handler = get_by_id_handler

    def create(self, new_product: ProductInput) -> ProductResponse:
        command = CreateProductCommand(**new_product.model_dump(exclude_none=True))
        product = self.create_handler.handle(command)
        return ProductResponse.model_validate(product)

    def update(self, id: int, product: ProductInput) -> Product:
        command = UpdateProductCommand(
            product_id=id, **product.model_dump(exclude_none=True)
        )
        product = self.update_handler.handle(command)
        return ProductResponse.model_validate(product)

    def delete(self, id: int) -> None:
        command = DeleteProductCommand(product_id=id)
        self.delete_handler.handle(command)

    def get_all(self) -> ProductsResponse:
        query = GetAllProductsQuery()
        products = self.get_all_handler.handle(query)
        data = [ProductResponse.model_validate(product) for product in products]
        return ProductsResponse(data=data)

    def get_by_id(self, id: int) -> ProductResponse:
        query = GetProductByIdQuery(product_id=id)
        product = self.get_by_id_handler.handle(query)
        if product is None:
            raise NotFoundError("Product not found")
        return ProductResponse.model_validate(product)
