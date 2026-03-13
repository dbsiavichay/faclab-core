from pydantic import AliasChoices, BaseModel, Field


class QuickCustomerRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128, description="Customer name")
    tax_id: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Tax ID (RUC/NIT)",
        validation_alias=AliasChoices("taxId", "tax_id"),
        serialization_alias="taxId",
    )
    tax_type: int = Field(
        1,
        ge=1,
        le=4,
        description="Tax type: 1=RUC, 2=NATIONAL_ID, 3=PASSPORT, 4=FOREIGN_ID",
        validation_alias=AliasChoices("taxType", "tax_type"),
        serialization_alias="taxType",
    )
