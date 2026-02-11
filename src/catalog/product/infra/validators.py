
from pydantic import AliasChoices, BaseModel, Field


# Inputs
class CategoryInput(BaseModel):
    name: str
    description: str | None = None


class ProductInput(BaseModel):
    name: str
    sku: str
    description: str | None = None
    category_id: int | None = Field(
        None,
        ge=1,
        description="Category ID (must be a positive integer)",
        validation_alias=AliasChoices("category_id", "categoryId"),
        serialization_alias="categoryId",
    )


# Responses
class CategoryResponse(CategoryInput):
    id: int = Field(ge=1, description="Category ID")


class ProductResponse(ProductInput):
    id: int = Field(ge=1, description="Product ID")


class ProductsResponse(BaseModel):
    data: list[ProductResponse] = Field(..., description="List of products")
