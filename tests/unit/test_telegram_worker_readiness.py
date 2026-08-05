from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.services.telegram_observability import (
    TelegramOperationalStatus,
    TelegramWorkerReadinessDependencies,
    create_configuration_environment_check,
    create_job_repository_contract_check,
    create_keyring_contract_check,
    create_processor_contract_check,
    create_productive_worker_readiness_service,
    create_receipt_repository_contract_check,
)


class FakeCursor:
    def __init__(
        self,
        row=(1,),
    ):
        self.row = row
        self.statements = []
        self.closed = False

    def execute(
        self,
        statement,
    ):
        self.statements.append(statement)

    def fetchone(
        self,
    ):
        return self.row

    def close(
        self,
    ):
        self.closed = True


class FakeConnection:
    def __init__(
        self,
        cursor,
    ):
        self._cursor = cursor
        self.closed = False

    def cursor(
        self,
    ):
        return self._cursor

    def close(
        self,
    ):
        self.closed = True


class FakeJobRepository:
    def claim_next_telegram_update_job(
        self,
        *,
        lock_token,
        lease_seconds=120,
    ):
        raise AssertionError("Método mutante não deve ser chamado.")


class FakeReceiptRepository:
    def claim_telegram_update(
        self,
        *,
        update_id,
        claim_token,
        lease_seconds,
    ):
        raise AssertionError("Método mutante não deve ser chamado.")


@dataclass
class FakeKeyring:
    active_key_id: str


class FakeMetricsRuntime:
    pass


def fake_processor(
    update,
):
    return update


def dependencies(
    *,
    configuration=True,
    database_row=(1,),
    metrics=True,
):
    cursor = FakeCursor(row=database_row)

    connection = FakeConnection(cursor)

    deps = TelegramWorkerReadinessDependencies(
        configuration_check=(lambda: configuration),
        database_connection_factory=(lambda: connection),
        job_repository_factory=(FakeJobRepository),
        receipt_repository_factory=(FakeReceiptRepository),
        keyring_factory=(lambda: FakeKeyring(active_key_id="key-v1")),
        processor_factory=(lambda: fake_processor),
        metrics_runtime_factory=((FakeMetricsRuntime) if metrics else (lambda: None)),
    )

    return deps, cursor, connection


def test_configuration_check_passes():
    check = create_configuration_environment_check(
        required_values={
            "DATABASE_URL": ("postgresql://configured"),
            "TELEGRAM_BOT_TOKEN": ("configured"),
        }
    )

    result = check()

    assert result == {
        "passed": True,
        "required_count": 2,
        "missing_count": 0,
    }


def test_configuration_check_reports_count_only():
    check = create_configuration_environment_check(
        required_values={
            "DATABASE_URL": "",
            "TELEGRAM_BOT_TOKEN": None,
        }
    )

    result = check()

    assert result == {
        "passed": False,
        "required_count": 2,
        "missing_count": 2,
    }

    rendered = repr(result)

    assert "DATABASE_URL" not in rendered
    assert "TELEGRAM_BOT_TOKEN" not in rendered


def test_job_repository_check_does_not_claim():
    result = create_job_repository_contract_check(FakeJobRepository)()

    assert result["passed"] is True

    assert result["callable"] is True


def test_receipt_repository_check_does_not_claim():
    result = create_receipt_repository_contract_check(FakeReceiptRepository)()

    assert result["passed"] is True

    assert result["callable"] is True


def test_keyring_check_does_not_expose_key_id():
    result = create_keyring_contract_check(
        lambda: FakeKeyring(active_key_id=("private-production-key"))
    )()

    assert result["passed"] is True

    assert "private-production-key" not in repr(result)


def test_processor_check_requires_callable():
    result = create_processor_contract_check(lambda: fake_processor)()

    assert result["passed"] is True

    assert result["callable"] is True


def test_processor_check_rejects_non_callable():
    result = create_processor_contract_check(lambda: object())()

    assert result["passed"] is False


def test_productive_readiness_is_healthy():
    deps, cursor, connection = dependencies()

    snapshot = create_productive_worker_readiness_service(deps).evaluate()

    assert snapshot.status is TelegramOperationalStatus.HEALTHY

    assert snapshot.ready is True

    assert cursor.statements == ["SELECT 1"]

    assert cursor.closed is True
    assert connection.closed is True


def test_metrics_unavailable_is_degraded():
    deps, _, _ = dependencies(metrics=False)

    snapshot = create_productive_worker_readiness_service(deps).evaluate()

    assert snapshot.status is TelegramOperationalStatus.DEGRADED

    assert snapshot.ready is True


def test_configuration_failure_is_unready():
    deps, _, _ = dependencies(configuration=False)

    snapshot = create_productive_worker_readiness_service(deps).evaluate()

    assert snapshot.status is TelegramOperationalStatus.UNREADY

    assert snapshot.ready is False


def test_database_invalid_response_is_unready():
    deps, _, _ = dependencies(database_row=(0,))

    snapshot = create_productive_worker_readiness_service(deps).evaluate()

    assert snapshot.status is TelegramOperationalStatus.UNREADY


def test_database_exception_is_safe():
    class BrokenCursor:
        def execute(
            self,
            statement,
        ):
            raise RuntimeError("postgresql://user:password@secret")

        def close(
            self,
        ):
            pass

    connection = FakeConnection(BrokenCursor())

    deps, _, _ = dependencies()

    broken = TelegramWorkerReadinessDependencies(
        configuration_check=(deps.configuration_check),
        database_connection_factory=(lambda: connection),
        job_repository_factory=(deps.job_repository_factory),
        receipt_repository_factory=(deps.receipt_repository_factory),
        keyring_factory=(deps.keyring_factory),
        processor_factory=(deps.processor_factory),
        metrics_runtime_factory=(deps.metrics_runtime_factory),
    )

    snapshot = create_productive_worker_readiness_service(broken).evaluate()

    rendered = repr(snapshot.to_safe_dict())

    assert snapshot.status is TelegramOperationalStatus.UNREADY

    assert "password" not in rendered
    assert "postgresql://" not in rendered


def test_metrics_probe_can_be_disabled():
    deps, _, _ = dependencies()

    without_metrics = TelegramWorkerReadinessDependencies(
        configuration_check=(deps.configuration_check),
        database_connection_factory=(deps.database_connection_factory),
        job_repository_factory=(deps.job_repository_factory),
        receipt_repository_factory=(deps.receipt_repository_factory),
        keyring_factory=(deps.keyring_factory),
        processor_factory=(deps.processor_factory),
        metrics_runtime_factory=None,
    )

    snapshot = create_productive_worker_readiness_service(without_metrics).evaluate()

    assert snapshot.status is TelegramOperationalStatus.HEALTHY

    assert len(snapshot.checks) == 6


@pytest.mark.parametrize(
    "factory",
    [
        lambda: create_job_repository_contract_check(lambda: object()),
        lambda: create_receipt_repository_contract_check(lambda: object()),
    ],
)
def test_missing_repository_contract_fails(
    factory,
):
    result = factory()()

    assert result["passed"] is False
