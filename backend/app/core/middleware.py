from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.exceptions import error_response


REQUEST_ID_STATE_KEY = "request_id"


def get_request_id(request: Request) -> str | None:
    return getattr(request.state, REQUEST_ID_STATE_KEY, None)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        incoming = request.headers.get(settings.request_id_header, "").strip()
        request_id = incoming[:128] if incoming else uuid4().hex
        setattr(request.state, REQUEST_ID_STATE_KEY, request_id)
        response = await call_next(request)
        response.headers[settings.request_id_header] = request_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        if not settings.security_headers_enabled:
            return response
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self'",
        )
        if settings.hsts_enabled:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response


@dataclass(frozen=True)
class RateLimitRule:
    limit: int
    window_seconds: int


_rate_limit_store: dict[str, deque[float]] = defaultdict(deque)


def reset_rate_limit_store() -> None:
    _rate_limit_store.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.rules = {
            ("POST", "/api/v1/auth/signup"): RateLimitRule(10, 60),
            ("POST", "/api/v1/auth/login"): RateLimitRule(10, 60),
            ("POST", "/api/v1/auth/refresh"): RateLimitRule(30, 60),
            ("POST", "/api/v1/auth/forgot-password"): RateLimitRule(5, 300),
            ("POST", "/api/v1/auth/resend-email-verification"): RateLimitRule(5, 300),
            ("POST", "/api/v1/recommendations/jobs/generate"): RateLimitRule(10, 60),
            ("POST", "/api/v1/recommendations/jobs/run-if-due"): RateLimitRule(10, 60),
            ("POST", "/api/v1/notifications/run-due"): RateLimitRule(20, 60),
        }

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        rule = self.rules.get((request.method.upper(), request.url.path))
        if not settings.rate_limit_enabled or rule is None:
            return await call_next(request)

        now = time.monotonic()
        client_host = request.client.host if request.client else "unknown"
        user_key = request.headers.get("authorization", client_host)
        key = f"{request.method}:{request.url.path}:{user_key}"
        bucket = _rate_limit_store[key]
        while bucket and bucket[0] <= now - rule.window_seconds:
            bucket.popleft()

        remaining = max(rule.limit - len(bucket), 0)
        if remaining <= 0:
            response = error_response(
                "RATE_LIMIT_EXCEEDED",
                "요청 횟수가 너무 많습니다. 잠시 후 다시 시도해 주세요.",
                429,
                request_id=get_request_id(request),
            )
            retry_after = max(1, int(rule.window_seconds - (now - bucket[0]))) if bucket else rule.window_seconds
            response.headers["Retry-After"] = str(retry_after)
            response.headers["X-RateLimit-Limit"] = str(rule.limit)
            response.headers["X-RateLimit-Remaining"] = "0"
            return response

        bucket.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rule.limit)
        response.headers["X-RateLimit-Remaining"] = str(max(rule.limit - len(bucket), 0))
        return response
