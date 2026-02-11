from decimal import Decimal

from pydantic import AliasChoices, BaseModel, Field


# Customer Inputs
class CustomerInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=128, description="Customer name")
    tax_id: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Tax ID (RUC/NIT)",
        validation_alias=AliasChoices("tax_id", "taxId"),
        serialization_alias="taxId",
    )
    tax_type: int = Field(
        1,
        ge=1,
        le=4,
        description="Tax type: 1=RUC, 2=NATIONAL_ID, 3=PASSPORT, 4=FOREIGN_ID",
        validation_alias=AliasChoices("tax_type", "taxType"),
        serialization_alias="taxType",
    )
    email: str | None = Field(None, max_length=128)
    phone: str | None = Field(None, max_length=32)
    address: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=64)
    state: str | None = Field(None, max_length=64)
    country: str | None = Field(None, max_length=64)
    credit_limit: Decimal | None = Field(
        None,
        ge=0,
        description="Credit limit",
        validation_alias=AliasChoices("credit_limit", "creditLimit"),
        serialization_alias="creditLimit",
    )
    payment_terms: int | None = Field(
        None,
        ge=0,
        description="Payment terms in days",
        validation_alias=AliasChoices("payment_terms", "paymentTerms"),
        serialization_alias="paymentTerms",
    )
    is_active: bool | None = Field(
        True,
        description="Customer active status",
        validation_alias=AliasChoices("is_active", "isActive"),
        serialization_alias="isActive",
    )


class CustomerContactInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=128, description="Contact name")
    role: str | None = Field(None, max_length=64)
    email: str | None = Field(None, max_length=128)
    phone: str | None = Field(None, max_length=32)


# Customer Responses
class CustomerResponse(BaseModel):
    id: int = Field(ge=1, description="Customer ID")
    name: str
    tax_id: str = Field(serialization_alias="taxId")
    tax_type: int = Field(serialization_alias="taxType")
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    credit_limit: Decimal | None = Field(None, serialization_alias="creditLimit")
    payment_terms: int | None = Field(None, serialization_alias="paymentTerms")
    is_active: bool = Field(serialization_alias="isActive")


class CustomerContactResponse(BaseModel):
    id: int = Field(ge=1, description="Contact ID")
    customer_id: int = Field(
        ge=1, description="Customer ID", serialization_alias="customerId"
    )
    name: str
    role: str | None = None
    email: str | None = None
    phone: str | None = None


class CustomersResponse(BaseModel):
    data: list[CustomerResponse] = Field(..., description="List of customers")


class CustomerContactsResponse(BaseModel):
    data: list[CustomerContactResponse] = Field(
        ..., description="List of customer contacts"
    )
