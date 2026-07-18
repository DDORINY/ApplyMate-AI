from datetime import datetime

from pydantic import BaseModel

from app.models.oauth import OAuthProvider
from app.schemas.auth import AuthTokenData


class OAuthProviderPublic(BaseModel):
    provider: OAuthProvider
    enabled: bool


class OAuthProvidersData(BaseModel):
    providers: list[OAuthProviderPublic]


class OAuthAuthorizationData(BaseModel):
    authorization_url: str


class OAuthExchangeRequest(BaseModel):
    ticket: str


class OAuthExchangeData(AuthTokenData):
    redirect_path: str
    provider: OAuthProvider


class OAuthAccountPublic(BaseModel):
    provider: OAuthProvider
    provider_email: str | None
    provider_username: str | None
    provider_display_name: str | None
    email_verified: bool
    created_at: datetime
    last_login_at: datetime | None
    can_unlink: bool


class OAuthAccountsData(BaseModel):
    accounts: list[OAuthAccountPublic]
