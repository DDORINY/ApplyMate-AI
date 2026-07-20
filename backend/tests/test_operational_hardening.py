import os

from fastapi.testclient import TestClient

os.environ["JWT_SECRET_KEY"] = "test-access-secret"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret"

from app.core.middleware import reset_rate_limit_store
from app.main import app


def test_rate_limit_returns_429_with_headers():
    reset_rate_limit_store()
    client = TestClient(app)

    last_response = None
    for _ in range(21):
        last_response = client.post("/api/v1/notifications/run-due")

    assert last_response is not None
    assert last_response.status_code == 429
    assert last_response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert last_response.headers["Retry-After"]
    assert last_response.headers["X-RateLimit-Limit"] == "20"
    assert last_response.headers["X-RateLimit-Remaining"] == "0"
    reset_rate_limit_store()


def test_cors_preflight_allows_configured_frontend_origin():
    client = TestClient(app)
    response = client.options(
        "/api/v1/health/live",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
