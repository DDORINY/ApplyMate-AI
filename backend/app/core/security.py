import base64
import hashlib
import hmac
import json
import re
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings
from app.core.exceptions import AppError

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_ITERATIONS = 210_000
REFRESH_TOKEN_COOKIE_NAME = "applymate_refresh_token"


def utc_now() -> datetime:
    return datetime.now(UTC)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_email(email: str) -> str:
    normalized = normalize_email(email)
    if not EMAIL_PATTERN.match(normalized):
        raise AppError("VALIDATION_ERROR", "이메일 형식이 올바르지 않습니다.", 422)
    return normalized


def validate_password(password: str) -> None:
    if len(password) < 8:
        raise AppError("VALIDATION_ERROR", "비밀번호는 8자 이상이어야 합니다.", 422)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PASSWORD_ITERATIONS)
    return (
        f"pbkdf2_sha256${PASSWORD_ITERATIONS}$"
        f"{base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"
    )


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, digest = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        expected = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), base64.b64decode(salt), int(iterations)
        )
        return hmac.compare_digest(base64.b64encode(expected).decode(), digest)
    except Exception:
        return False


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64decode(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode())


def _secret_for(token_type: str) -> str:
    secret = settings.jwt_secret_key if token_type == "access" else settings.jwt_refresh_secret_key
    if not secret:
        raise AppError("AUTH_UNAUTHORIZED", "인증 설정이 완료되지 않았습니다.", 500)
    return secret


def create_jwt(
    subject: int, token_type: str, expires_delta: timedelta, jti: str | None = None
) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = utc_now()
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    if jti:
        payload["jti"] = jti

    signing_input = ".".join(
        [
            _b64encode(json.dumps(header, separators=(",", ":")).encode()),
            _b64encode(json.dumps(payload, separators=(",", ":")).encode()),
        ]
    )
    signature = hmac.new(_secret_for(token_type).encode(), signing_input.encode(), hashlib.sha256)
    return f"{signing_input}.{_b64encode(signature.digest())}"


def decode_jwt(token: str, expected_type: str) -> dict[str, Any]:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}"
        expected_signature = hmac.new(
            _secret_for(expected_type).encode(), signing_input.encode(), hashlib.sha256
        ).digest()
        if not hmac.compare_digest(_b64encode(expected_signature), signature_b64):
            raise AppError("AUTH_TOKEN_INVALID", "유효하지 않은 토큰입니다.", 401)

        payload = json.loads(_b64decode(payload_b64))
        if payload.get("type") != expected_type:
            raise AppError("AUTH_TOKEN_INVALID", "유효하지 않은 토큰입니다.", 401)
        if int(payload["exp"]) < int(utc_now().timestamp()):
            code = (
                "AUTH_TOKEN_EXPIRED" if expected_type == "access" else "AUTH_REFRESH_TOKEN_EXPIRED"
            )
            raise AppError(code, "토큰이 만료되었습니다.", 401)
        return payload
    except AppError:
        raise
    except Exception as exc:
        code = "AUTH_TOKEN_INVALID" if expected_type == "access" else "AUTH_REFRESH_TOKEN_INVALID"
        raise AppError(code, "유효하지 않은 토큰입니다.", 401) from exc


def create_access_token(user_id: int) -> str:
    return create_jwt(user_id, "access", timedelta(minutes=settings.access_token_expire_minutes))


def create_refresh_token(user_id: int) -> tuple[str, str, datetime]:
    jti = secrets.token_urlsafe(24)
    expires_at = utc_now() + timedelta(days=settings.refresh_token_expire_days)
    return create_jwt(user_id, "refresh", expires_at - utc_now(), jti), jti, expires_at
