from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.shared.infra.validators import QueryParams


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(
        ...,
        min_length=1,
        validation_alias=AliasChoices("refreshToken", "refresh_token"),
        serialization_alias="refreshToken",
    )


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)


class TokenPairResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    access_token: str = Field(description="Short-lived access token")
    refresh_token: str = Field(description="Long-lived refresh token")
    token_type: str = Field("Bearer", description="Token scheme")
    expires_in: int = Field(description="Access token lifetime in seconds")


class AuthenticatedUserResponse(BaseModel):
    id: int = Field(ge=1)
    username: str
    role: int = Field(
        description="Role code (1=ADMIN, 2=MANAGER, 3=OPERATOR, 4=VIEWER)"
    )
    permissions: list[str] = Field(default_factory=list)


class CreateUserRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    username: str = Field(..., min_length=1, max_length=64)
    email: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=8, max_length=128)
    role: int = Field(
        4,
        ge=1,
        le=4,
        description="Role code (1=ADMIN, 2=MANAGER, 3=OPERATOR, 4=VIEWER)",
    )


class UpdateUserRoleRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    role: int = Field(
        ...,
        ge=1,
        le=4,
        description="Role code (1=ADMIN, 2=MANAGER, 3=OPERATOR, 4=VIEWER)",
    )


class UserResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    username: str
    email: str
    role: int = Field(
        description="Role code (1=ADMIN, 2=MANAGER, 3=OPERATOR, 4=VIEWER)"
    )
    is_active: bool
    last_login_at: datetime | None = None
    created_at: datetime | None = None


class UserQueryParams(QueryParams):
    is_active: bool | None = Field(None, description="Filter by active status")
    role: int | None = Field(None, ge=1, le=4, description="Filter by role")
