from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "probe": "health",
        "ready": True,
        "schema_version": (
            "telegram-operational-status.v1"
        ),
        "status": "healthy",
    }

    assert (
        response.headers["cache-control"]
        == "no-store"
    )
