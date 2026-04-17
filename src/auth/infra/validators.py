from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


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
