import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_env: str
    frontend_url: str
    backend_url: str
    database_url: str
    redis_url: str
    jwt_secret_key: str
    jwt_refresh_secret_key: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    cookie_secure: bool
    cookie_samesite: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        frontend_url=os.getenv("FRONTEND_URL", "http://localhost:3000"),
        backend_url=os.getenv("BACKEND_URL", "http://localhost:8000"),
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://applymate:change_me@localhost:5432/applymate",
        ),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY", ""),
        jwt_refresh_secret_key=os.getenv("JWT_REFRESH_SECRET_KEY", ""),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        refresh_token_expire_days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "14")),
        cookie_secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        cookie_samesite=os.getenv("COOKIE_SAMESITE", "lax"),
    )


settings = get_settings()
