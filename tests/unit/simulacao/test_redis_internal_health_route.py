from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_internal_redis_health_requires_trusted_context():
    response = client.get(
        "/internal/redis/health"
    )

    assert response.status_code in {
        401,
        403,
        422,
    }


def test_internal_redis_health_returns_status():
    app.dependency_overrides.clear()

    from api.security import (
        TrustedRequestContext,
        require_trusted_request_context,
    )

    def fake_trusted_context():
        return TrustedRequestContext(
            user_id="internal:test",
            request_id="internal-request:test",
            timestamp=1_700_000_000,
        )

    app.dependency_overrides[
        require_trusted_request_context
    ] = fake_trusted_context

    try:
        with (
            patch(
                "api.main.is_redis_configured",
                return_value=True,
            ),
            patch(
                "api.main.ping_redis",
                return_value=True,
            ),
        ):
            response = client.get(
                "/internal/redis/health"
            )

        assert response.status_code == 200

        body = response.json()

        assert body == {
            "configured": True,
            "reachable": True,
        }
    finally:
        app.dependency_overrides.clear()


def test_internal_redis_health_fail_open_when_unconfigured():
    app.dependency_overrides.clear()

    from api.security import (
        TrustedRequestContext,
        require_trusted_request_context,
    )

    def fake_trusted_context():
        return TrustedRequestContext(
            user_id="internal:test",
            request_id="internal-request:test",
            timestamp=1_700_000_000,
        )

    app.dependency_overrides[
        require_trusted_request_context
    ] = fake_trusted_context

    try:
        with (
            patch(
                "api.main.is_redis_configured",
                return_value=False,
            ),
            patch(
                "api.main.ping_redis",
            ) as mocked_ping,
        ):
            response = client.get(
                "/internal/redis/health"
            )

        assert response.status_code == 200

        assert response.json() == {
            "configured": False,
            "reachable": False,
        }

        mocked_ping.assert_not_called()
    finally:
        app.dependency_overrides.clear()
