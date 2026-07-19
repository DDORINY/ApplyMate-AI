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
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    github_client_id: str
    github_client_secret: str
    github_redirect_uri: str
    oauth_frontend_callback_url: str
    oauth_allowed_redirect_paths: tuple[str, ...]
    oauth_state_expire_seconds: int
    oauth_ticket_expire_seconds: int
    email_provider: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool
    email_from_address: str
    email_from_name: str
    frontend_email_verify_url: str
    frontend_password_reset_url: str
    email_verification_expire_minutes: int
    password_reset_expire_minutes: int
    email_resend_cooldown_seconds: int
    login_max_failed_attempts: int
    login_lockout_seconds: int
    ai_provider: str
    openai_api_key: str
    openai_model: str
    ai_request_timeout_seconds: int
    ai_max_retries: int
    ai_analysis_max_input_chars: int
    ai_analysis_prompt_version: str
    ai_analysis_schema_version: str
    ai_store_raw_response: bool
    ai_daily_analysis_limit: int
    ai_analysis_cooldown_seconds: int
    resume_storage_dir: str
    resume_max_file_size_bytes: int
    resume_allowed_extensions: tuple[str, ...]
    resume_allowed_content_types: tuple[str, ...]
    calendar_provider: str
    google_calendar_client_id: str
    google_calendar_client_secret: str
    google_calendar_redirect_uri: str
    google_calendar_scopes: tuple[str, ...]
    external_token_encryption_key: str
    external_token_encryption_key_version: str
    calendar_oauth_state_expire_seconds: int


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
        google_client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
        google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
        google_redirect_uri=os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/api/v1/auth/oauth/google/callback",
        ),
        github_client_id=os.getenv("GITHUB_CLIENT_ID", ""),
        github_client_secret=os.getenv("GITHUB_CLIENT_SECRET", ""),
        github_redirect_uri=os.getenv(
            "GITHUB_REDIRECT_URI",
            "http://localhost:8000/api/v1/auth/oauth/github/callback",
        ),
        oauth_frontend_callback_url=os.getenv(
            "OAUTH_FRONTEND_CALLBACK_URL",
            "http://localhost:3000/auth/callback",
        ),
        oauth_allowed_redirect_paths=tuple(
            item.strip()
            for item in os.getenv(
                "OAUTH_ALLOWED_REDIRECT_PATHS", "/me,/profile,/settings/accounts"
            ).split(",")
            if item.strip()
        ),
        oauth_state_expire_seconds=int(os.getenv("OAUTH_STATE_EXPIRE_SECONDS", "300")),
        oauth_ticket_expire_seconds=int(os.getenv("OAUTH_TICKET_EXPIRE_SECONDS", "60")),
        email_provider=os.getenv("EMAIL_PROVIDER", "development"),
        smtp_host=os.getenv("SMTP_HOST", ""),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_username=os.getenv("SMTP_USERNAME", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        smtp_use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
        email_from_address=os.getenv("EMAIL_FROM_ADDRESS", ""),
        email_from_name=os.getenv("EMAIL_FROM_NAME", "ApplyMate AI"),
        frontend_email_verify_url=os.getenv(
            "FRONTEND_EMAIL_VERIFY_URL", "http://localhost:3000/verify-email"
        ),
        frontend_password_reset_url=os.getenv(
            "FRONTEND_PASSWORD_RESET_URL", "http://localhost:3000/reset-password"
        ),
        email_verification_expire_minutes=int(os.getenv("EMAIL_VERIFICATION_EXPIRE_MINUTES", "30")),
        password_reset_expire_minutes=int(os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", "30")),
        email_resend_cooldown_seconds=int(os.getenv("EMAIL_RESEND_COOLDOWN_SECONDS", "60")),
        login_max_failed_attempts=int(os.getenv("LOGIN_MAX_FAILED_ATTEMPTS", "5")),
        login_lockout_seconds=int(os.getenv("LOGIN_LOCKOUT_SECONDS", "900")),
        ai_provider=os.getenv("AI_PROVIDER", "disabled").strip().lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", ""),
        ai_request_timeout_seconds=int(os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "60")),
        ai_max_retries=int(os.getenv("AI_MAX_RETRIES", "2")),
        ai_analysis_max_input_chars=int(os.getenv("AI_ANALYSIS_MAX_INPUT_CHARS", "30000")),
        ai_analysis_prompt_version=os.getenv("AI_ANALYSIS_PROMPT_VERSION", "v1"),
        ai_analysis_schema_version=os.getenv("AI_ANALYSIS_SCHEMA_VERSION", "v1"),
        ai_store_raw_response=os.getenv("AI_STORE_RAW_RESPONSE", "false").lower() == "true",
        ai_daily_analysis_limit=int(os.getenv("AI_DAILY_ANALYSIS_LIMIT", "20")),
        ai_analysis_cooldown_seconds=int(os.getenv("AI_ANALYSIS_COOLDOWN_SECONDS", "30")),
        resume_storage_dir=os.getenv("RESUME_STORAGE_DIR", "storage/resumes"),
        resume_max_file_size_bytes=int(os.getenv("RESUME_MAX_FILE_SIZE_BYTES", "5242880")),
        resume_allowed_extensions=tuple(
            item.strip().lower()
            for item in os.getenv("RESUME_ALLOWED_EXTENSIONS", ".pdf,.docx").split(",")
            if item.strip()
        ),
        resume_allowed_content_types=tuple(
            item.strip().lower()
            for item in os.getenv(
                "RESUME_ALLOWED_CONTENT_TYPES",
                "application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ).split(",")
            if item.strip()
        ),
        calendar_provider=os.getenv("CALENDAR_PROVIDER", "disabled").strip().lower(),
        google_calendar_client_id=os.getenv("GOOGLE_CALENDAR_CLIENT_ID", ""),
        google_calendar_client_secret=os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET", ""),
        google_calendar_redirect_uri=os.getenv(
            "GOOGLE_CALENDAR_REDIRECT_URI",
            "http://localhost:8000/api/v1/integrations/calendar/callback",
        ),
        google_calendar_scopes=tuple(
            item.strip()
            for item in os.getenv(
                "GOOGLE_CALENDAR_SCOPES",
                "openid,email,profile,https://www.googleapis.com/auth/calendar.calendarlist.readonly,"
                "https://www.googleapis.com/auth/calendar.events",
            ).split(",")
            if item.strip()
        ),
        external_token_encryption_key=os.getenv("EXTERNAL_TOKEN_ENCRYPTION_KEY", ""),
        external_token_encryption_key_version=os.getenv("EXTERNAL_TOKEN_ENCRYPTION_KEY_VERSION", "v1"),
        calendar_oauth_state_expire_seconds=int(os.getenv("CALENDAR_OAUTH_STATE_EXPIRE_SECONDS", "300")),
    )


settings = get_settings()
