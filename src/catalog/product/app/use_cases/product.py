from typing import Optional

from src.catalog.product.app.types import ProductInput, ProductOutput
from src.catalog.product.domain.entities import Product
from src.shared.app.repositories import Repository


class CreateProductUseCase:
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def execute(self, product_create: ProductInput) -> ProductOutput:
        product = Product(**product_create)
        product = self.repo.create(product)
        return product.dict()


class UpdateProductUseCase:
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def execute(self, id: int, product_update: ProductInput) -> ProductOutput:
        product = Product(id=id, **product_update)
        product = self.repo.update(product)
        return product.dict()


class DeleteProductUseCase:
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def execute(self, id: int) -> None:
        return self.repo.delete(id)


class GetProductByIdUseCase:
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def execute(self, id: int) -> Optional[ProductOutput]:
        product = self.repo.get_by_id(id)
        if product is None:
            return None
        return product.dict()


class GetAllProductsUseCase:
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def execute(self) -> list[ProductOutput]:
        products = self.repo.get_all()
        return [product.dict() for product in products]
