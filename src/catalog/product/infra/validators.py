from pydantic import AliasChoices, BaseModel, Field


# Requests
class CategoryRequest(BaseModel):
    name: str
    description: str | None = None


class ProductRequest(BaseModel):
    name: str
    sku: str
    description: str | None = None
    category_id: int | None = Field(
        None,
        ge=1,
        description="Category ID (must be a positive integer)",
        validation_alias=AliasChoices("categoryId", "category_id"),
        serialization_alias="categoryId",
    )


# Responses
class CategoryResponse(CategoryRequest):
    id: int = Field(ge=1, description="Category ID")


class ProductResponse(ProductRequest):
    id: int = Field(ge=1, description="Product ID")


class ProductsResponse(BaseModel):
    data: list[ProductResponse] = Field(..., description="List of products")
