from unittest.mock import MagicMock, patch

from src.cache.redis_client import (
    get_redis_client,
    is_redis_configured,
    ping_redis,
    reset_redis_client,
)


def setup_function():
    reset_redis_client()


def teardown_function():
    reset_redis_client()


def test_redis_not_configured_is_fail_open(
    monkeypatch,
):
    monkeypatch.delenv(
        "INNA_REDIS_URL",
        raising=False,
    )

    assert is_redis_configured() is False
    assert get_redis_client() is None
    assert ping_redis() is False


def test_redis_configured_creates_client(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_REDIS_URL",
        "redis://localhost:6379/0",
    )

    fake_client = MagicMock()

    with patch(
        "src.cache.redis_client.redis.Redis.from_url",
        return_value=fake_client,
    ) as mocked_from_url:
        client = get_redis_client()

    assert client is fake_client
    mocked_from_url.assert_called_once()


def test_ping_redis_returns_true(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_REDIS_URL",
        "redis://localhost:6379/0",
    )

    fake_client = MagicMock()
    fake_client.ping.return_value = True

    with patch(
        "src.cache.redis_client.redis.Redis.from_url",
        return_value=fake_client,
    ):
        assert ping_redis() is True


def test_redis_client_creation_failure_is_fail_open(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_REDIS_URL",
        "redis://localhost:6379/0",
    )

    with patch(
        "src.cache.redis_client.redis.Redis.from_url",
        side_effect=RuntimeError("boom"),
    ):
        assert get_redis_client() is None


def test_reset_redis_client_recreates_client(
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_REDIS_URL",
        "redis://localhost:6379/0",
    )

    first = MagicMock()
    second = MagicMock()

    with patch(
        "src.cache.redis_client.redis.Redis.from_url",
        side_effect=[first, second],
    ):
        assert get_redis_client() is first
        assert get_redis_client() is first

        reset_redis_client()

        assert get_redis_client() is second
