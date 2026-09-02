import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return normalize_email(value)


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    role: UserRole
    is_active: bool


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=12, max_length=128)
    role: UserRole

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return normalize_email(value)


class UserUpdate(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None


def normalize_email(value: str) -> str:
    normalized = value.strip().lower()
    if normalized.count("@") != 1 or normalized.startswith("@") or normalized.endswith("@"):
        raise ValueError("invalid email address")
    return normalized
