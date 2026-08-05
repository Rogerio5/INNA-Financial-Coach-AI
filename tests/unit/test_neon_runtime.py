from contextlib import contextmanager

from src.observability import neon_runtime


class FakeCursor:
    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return False

    def execute(self, sql):
        self.sql = sql

    def fetchone(self):
        return (1, "17.5")


class FakeConnection:
    def cursor(self):
        return FakeCursor()


class FakePool:
    closed = False

    def get_stats(self):
        return {
            "pool_size": 4,
            "pool_available": 3,
            "requests_waiting": 0,
        }

    @contextmanager
    def connection(self, timeout):
        assert timeout == 5.0
        yield FakeConnection()


def test_collect_neon_runtime_status_success(
    monkeypatch,
):
    monkeypatch.setattr(
        neon_runtime,
        "obter_pool_postgres",
        lambda: FakePool(),
    )

    status = neon_runtime.collect_neon_runtime_status()

    assert status.configured is True
    assert status.available is True
    assert status.server_version == "17.5"
    assert status.pool_status == "healthy"
    assert status.pool_size == 4
    assert status.pool_available == 3
    assert status.pool_waiting == 0
    assert status.latency_ms is not None
    assert status.error_type is None


def test_collect_neon_runtime_status_handles_failure(
    monkeypatch,
):
    def raise_connection_error():
        raise RuntimeError("credencial ou endereço privado")

    monkeypatch.setattr(
        neon_runtime,
        "obter_pool_postgres",
        raise_connection_error,
    )

    status = neon_runtime.collect_neon_runtime_status()

    assert status.configured is False
    assert status.available is False
    assert status.pool_status == "unavailable"
    assert status.error_type == "RuntimeError"

    payload = status.to_dict()

    assert "credencial" not in str(payload)
    assert "endereço privado" not in str(payload)


class FakeDictCursor(FakeCursor):
    def fetchone(self):
        return {
            "health_check": 1,
            "server_version": "17.5",
        }


class FakeDictConnection:
    def cursor(self):
        return FakeDictCursor()


class FakeDictPool(FakePool):
    @contextmanager
    def connection(self, timeout):
        assert timeout == 5.0
        yield FakeDictConnection()


def test_collect_neon_runtime_accepts_dict_row(
    monkeypatch,
):
    monkeypatch.setattr(
        neon_runtime,
        "obter_pool_postgres",
        lambda: FakeDictPool(),
    )

    status = neon_runtime.collect_neon_runtime_status()

    assert status.configured is True
    assert status.available is True
    assert status.server_version == "17.5"
    assert status.pool_status == "healthy"
    assert status.error_type is None
