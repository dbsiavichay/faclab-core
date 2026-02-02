from typing import List

from src.core.infra.exceptions import NotFoundException
from src.product.app.use_cases import (
    CreateCategoryUseCase,
    CreateProductUseCase,
    DeleteCategoryUseCase,
    DeleteProductUseCase,
    GetAllCategoriesUseCase,
    GetAllProductsUseCase,
    GetCategoryByIdUseCase,
    GetProductByIdUseCase,
    UpdateCategoryUseCase,
    UpdateProductUseCase,
)
from src.product.domain.entities import Product
from src.product.infra.validators import (
    CategoryInput,
    CategoryResponse,
    ProductInput,
    ProductResponse,
    ProductsResponse,
)


class CategoryController:
    def __init__(
        self,
        create_category: CreateCategoryUseCase,
        update_category: UpdateCategoryUseCase,
        delete_category: DeleteCategoryUseCase,
        get_all_categories: GetAllCategoriesUseCase,
        get_category_by_id: GetCategoryByIdUseCase,
    ):
        self.create_category = create_category
        self.update_category = update_category
        self.delete_category = delete_category
        self.get_all_categories = get_all_categories
        self.get_category_by_id = get_category_by_id

    def create(self, new_category: CategoryInput) -> CategoryResponse:
        category = self.create_category.execute(
            new_category.model_dump(exclude_none=True)
        )
        return CategoryResponse.model_validate(category)

    def update(self, id: int, category: CategoryInput) -> Product:
        category = self.update_category.execute(
            id, category.model_dump(exclude_none=True)
        )
        return CategoryResponse.model_validate(category)

    def delete(self, id: int) -> None:
        self.delete_category.execute(id)

    def get_all(self) -> List[CategoryResponse]:
        categories = self.get_all_categories.execute()
        return [CategoryResponse.model_validate(category) for category in categories]

    def get_by_id(self, id: int) -> CategoryResponse:
        category = self.get_category_by_id.execute(id)
        if category is None:
            raise NotFoundException("Category not found")
        return CategoryResponse.model_validate(category)


class ProductController:
    def __init__(
        self,
        create_product: CreateProductUseCase,
        update_product: UpdateProductUseCase,
        delete_product: DeleteProductUseCase,
        get_all_products: GetAllProductsUseCase,
        get_product_by_id: GetProductByIdUseCase,
    ):
        self.create_product = create_product
        self.update_product = update_product
        self.delete_product = delete_product
        self.get_all_products = get_all_products
        self.get_product_by_id = get_product_by_id

    def create(self, new_product: ProductInput) -> ProductResponse:
        product = self.create_product.execute(new_product.model_dump(exclude_none=True))
        return ProductResponse.model_validate(product)

    def update(self, id: int, product: ProductInput) -> Product:
        product = self.update_product.execute(id, product.model_dump(exclude_none=True))
        return ProductResponse.model_validate(product)

    def delete(self, id: int) -> None:
        self.delete_product.execute(id)

    def get_all(self) -> ProductsResponse:
        products = self.get_all_products.execute()
        data = [ProductResponse.model_validate(product) for product in products]
        return ProductsResponse(data=data)

    def get_by_id(self, id: int) -> ProductResponse:
        product = self.get_product_by_id.execute(id)
        if product is None:
            raise NotFoundException("Product not found")
        return ProductResponse.model_validate(product)
