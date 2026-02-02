from typing import NotRequired, TypedDict


class CategoryBase(TypedDict):
    name: str
    description: NotRequired[str]


class CategoryInput(CategoryBase):
    pass


class CategoryOutput(CategoryBase):
    id: int


class ProductBase(TypedDict):
    name: str
    sku: str
    description: NotRequired[str]
    category_id: NotRequired[int]


class ProductInput(ProductBase):
    pass


class ProductOutput(ProductBase):
    id: int
