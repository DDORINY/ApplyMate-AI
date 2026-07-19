import base64
import hashlib
import hmac
import secrets

from app.core.config import get_settings
from app.core.exceptions import AppError


class ExternalTokenCipher:
    """Small stdlib-based authenticated token wrapper.

    This avoids adding a new dependency for v0.5.0 while keeping plaintext tokens
    out of the database. Production deployments should provide a high-entropy key
    through EXTERNAL_TOKEN_ENCRYPTION_KEY and rotate by version.
    """

    def __init__(self, key: str | None = None) -> None:
        settings = get_settings()
        self.key = (key if key is not None else settings.external_token_encryption_key).encode()
        self.version = settings.external_token_encryption_key_version

    def encrypt(self, value: str) -> str:
        if not self.key:
            raise AppError(
                "CALENDAR_TOKEN_ENCRYPTION_FAILED",
                "External token encryption key is not configured.",
                503,
            )
        nonce = secrets.token_bytes(16)
        plaintext = value.encode()
        stream = self._stream(nonce, len(plaintext))
        ciphertext = bytes(item ^ stream[index] for index, item in enumerate(plaintext))
        signature = hmac.new(self.key, nonce + ciphertext, hashlib.sha256).digest()
        payload = base64.urlsafe_b64encode(nonce + signature + ciphertext).decode()
        return f"{self.version}:{payload}"

    def decrypt(self, value: str) -> str:
        if not self.key:
            raise AppError(
                "CALENDAR_TOKEN_ENCRYPTION_FAILED",
                "External token encryption key is not configured.",
                503,
            )
        try:
            _version, payload = value.split(":", 1)
            raw = base64.urlsafe_b64decode(payload.encode())
            nonce = raw[:16]
            signature = raw[16:48]
            ciphertext = raw[48:]
        except Exception as exc:
            raise AppError("CALENDAR_TOKEN_ENCRYPTION_FAILED", "Encrypted token payload is invalid.", 503) from exc
        expected = hmac.new(self.key, nonce + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected):
            raise AppError("CALENDAR_TOKEN_ENCRYPTION_FAILED", "Encrypted token signature is invalid.", 503)
        stream = self._stream(nonce, len(ciphertext))
        plaintext = bytes(item ^ stream[index] for index, item in enumerate(ciphertext))
        return plaintext.decode()

    def _stream(self, nonce: bytes, length: int) -> bytes:
        output = b""
        counter = 0
        while len(output) < length:
            output += hmac.new(self.key, nonce + counter.to_bytes(4, "big"), hashlib.sha256).digest()
            counter += 1
        return output[:length]
