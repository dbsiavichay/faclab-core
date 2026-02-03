from typing import List, Optional

from pydantic import AliasChoices, BaseModel, Field


# Inputs
class CategoryInput(BaseModel):
    name: str
    description: Optional[str] = None


class ProductInput(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    category_id: Optional[int] = Field(
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
    data: List[ProductResponse] = Field(..., description="List of products")
