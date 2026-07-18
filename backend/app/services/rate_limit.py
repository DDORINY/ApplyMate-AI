from dataclasses import dataclass
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.security import hash_token, utc_now


@dataclass
class LoginFailureState:
    count: int
    locked_until: datetime | None


_login_failures: dict[str, LoginFailureState] = {}


def reset_login_rate_limit_store() -> None:
    _login_failures.clear()


class LoginRateLimiter:
    """Small account lockout helper.

    Redis integration can be swapped in behind this class; the in-memory store keeps local
    tests deterministic and avoids introducing secret-bearing infrastructure into unit tests.
    """

    def key_for(self, email: str) -> str:
        return hash_token(email)

    def check(self, email: str) -> None:
        state = _login_failures.get(self.key_for(email))
        if not state or not state.locked_until:
            return
        if state.locked_until <= utc_now():
            _login_failures.pop(self.key_for(email), None)
            return
        raise AppError(
            "AUTH_LOGIN_RATE_LIMITED",
            "로그인 실패 횟수가 많아 잠시 후 다시 시도해 주세요.",
            429,
        )

    def record_failure(self, email: str) -> None:
        key = self.key_for(email)
        state = _login_failures.get(key) or LoginFailureState(count=0, locked_until=None)
        state.count += 1
        if state.count >= settings.login_max_failed_attempts:
            state.locked_until = utc_now() + timedelta(seconds=settings.login_lockout_seconds)
        _login_failures[key] = state

    def reset(self, email: str) -> None:
        _login_failures.pop(self.key_for(email), None)
