from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.core.security import normalize_email
from app.models.user import UserStatus


class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def normalize_signup_email(cls, value: str) -> str:
        return normalize_email(value)


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_login_email(cls, value: str) -> str:
        return normalize_email(value)


class UserPublic(BaseModel):
    id: int
    email: str
    name: str
    status: UserStatus
    email_verified: bool
    last_login_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthTokenData(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserPublic
