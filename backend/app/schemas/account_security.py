from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.core.security import normalize_email
from app.models.account_security import SecurityEventType


class EmailVerificationSendData(BaseModel):
    sent: bool
    email: str


class EmailVerificationVerifyRequest(BaseModel):
    token: str = Field(min_length=16)


class EmailVerificationVerifyData(BaseModel):
    verified: bool


class ForgotPasswordRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def normalize_forgot_email(cls, value: str) -> str:
        return normalize_email(value)


class ForgotPasswordData(BaseModel):
    accepted: bool


class PasswordResetRequest(BaseModel):
    token: str = Field(min_length=16)
    new_password: str = Field(min_length=8, max_length=128)
    new_password_confirm: str = Field(min_length=8, max_length=128)


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)
    new_password_confirm: str = Field(min_length=8, max_length=128)


class PasswordSetRequest(BaseModel):
    new_password: str = Field(min_length=8, max_length=128)
    new_password_confirm: str = Field(min_length=8, max_length=128)


class PasswordUpdatedData(BaseModel):
    updated: bool


class SessionPublic(BaseModel):
    session_id: str
    device_name: str | None
    device_info: str | None
    user_agent: str | None
    current: bool
    created_at: datetime
    last_used_at: datetime | None
    expires_at: datetime


class SessionsData(BaseModel):
    sessions: list[SessionPublic]


class SessionRevokedData(BaseModel):
    revoked: bool
    revoked_count: int


class SecurityEventPublic(BaseModel):
    id: int
    event_type: SecurityEventType
    session_id: str | None
    event_metadata: dict[str, object]
    created_at: datetime

    model_config = {"from_attributes": True}


class SecurityEventsData(BaseModel):
    events: list[SecurityEventPublic]
