from fastapi.testclient import TestClient

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


def test_unknown_api_path_returns_common_error():
    client = TestClient(app)
    response = client.get("/api/v1/unknown")

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "error": {
            "code": "RESOURCE_NOT_FOUND",
            "message": "요청한 경로를 찾을 수 없습니다.",
        },
    }
