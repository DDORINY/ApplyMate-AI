import os

from fastapi.testclient import TestClient

os.environ["JWT_SECRET_KEY"] = "test-access-secret"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret"

from app.main import app


def test_health_response_structure(monkeypatch):
    async def fake_database_status() -> str:
        return "UP"

    async def fake_redis_status() -> str:
        return "UP"

    monkeypatch.setattr("app.api.v1.endpoints.health.check_database", fake_database_status)
    monkeypatch.setattr("app.api.v1.endpoints.health.check_redis", fake_redis_status)

    client = TestClient(app)
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "status": "UP",
            "database": "UP",
            "redis": "UP",
            "required_settings": "UP",
        },
        "message": "서비스가 정상적으로 실행 중입니다.",
    }


def test_health_returns_down_for_dependency_failures(monkeypatch):
    async def fake_database_status() -> str:
        return "DOWN"

    async def fake_redis_status() -> str:
        return "DOWN"

    monkeypatch.setattr("app.api.v1.endpoints.health.check_database", fake_database_status)
    monkeypatch.setattr("app.api.v1.endpoints.health.check_redis", fake_redis_status)

    client = TestClient(app)
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["database"] == "DOWN"
    assert body["data"]["redis"] == "DOWN"
    assert body["data"]["status"] == "DOWN"


def test_live_and_ready_health_endpoints(monkeypatch):
    async def fake_database_status() -> str:
        return "UP"

    async def fake_redis_status() -> str:
        return "UP"

    monkeypatch.setattr("app.api.v1.endpoints.health.check_database", fake_database_status)
    monkeypatch.setattr("app.api.v1.endpoints.health.check_redis", fake_redis_status)

    client = TestClient(app)

    live = client.get("/api/v1/health/live")
    ready = client.get("/api/v1/health/ready")

    assert live.status_code == 200
    assert live.json()["data"]["status"] == "UP"
    assert ready.status_code == 200
    assert ready.json()["data"]["status"] == "UP"


def test_unknown_api_path_returns_common_error():
    client = TestClient(app)
    response = client.get("/api/v1/unknown")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert body["error"]["message"] == "요청한 경로를 찾을 수 없습니다."
    assert body["error"]["request_id"]


def test_request_id_and_security_headers_are_added():
    client = TestClient(app)
    response = client.get("/api/v1/health/live", headers={"X-Request-ID": "test-request-id"})

    assert response.headers["X-Request-ID"] == "test-request-id"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
