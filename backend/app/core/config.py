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
    )


settings = get_settings()
