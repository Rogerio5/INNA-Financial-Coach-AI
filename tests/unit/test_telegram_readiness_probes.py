from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.services.telegram_observability import (
    TelegramOperationalStatus,
    TelegramProbeSeverity,
    TelegramWorkerReadinessChecks,
    create_attribute_readiness_check,
    create_callable_attribute_check,
    create_database_readiness_probe,
    create_database_select_check,
    create_factory_readiness_check,
    create_metrics_runtime_readiness_probe,
    create_worker_readiness_service,
)


class FakeCursor:
    def __init__(
        self,
        *,
        row=(1,),
        fail=False,
    ):
        self.row = row
        self.fail = fail
        self.executed = []
        self.closed = False

    def execute(
        self,
        statement,
    ):
        if self.fail:
            raise RuntimeError("private database exception")

        self.executed.append(statement)

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


@dataclass
class FakeKeyring:
    active_key_id: str


class FakeRepository:
    def find_by_update_id(
        self,
        update_id,
    ):
        return None


def healthy_checks(
    *,
    metrics=True,
):
    return TelegramWorkerReadinessChecks(
        configuration=lambda: {
            "passed": True,
            "environment": "configured",
        },
        database=lambda: {
            "passed": True,
            "driver": "postgresql",
        },
        job_repository=lambda: True,
        receipt_repository=lambda: True,
        keyring=lambda: {
            "passed": True,
            "active_key": True,
        },
        processor=lambda: {
            "passed": True,
            "callable": True,
        },
        metrics_runtime=(lambda: metrics),
    )


def test_database_probe_is_required():
    result = create_database_readiness_probe(lambda: True).run()

    assert result.passed

    assert result.severity is TelegramProbeSeverity.REQUIRED


def test_metrics_probe_is_optional():
    result = create_metrics_runtime_readiness_probe(lambda: False).run()

    assert not result.passed

    assert result.severity is TelegramProbeSeverity.OPTIONAL


def test_all_dependencies_healthy():
    snapshot = create_worker_readiness_service(healthy_checks()).evaluate()

    assert snapshot.status is TelegramOperationalStatus.HEALTHY

    assert snapshot.ready is True

    assert len(snapshot.checks) == 7


def test_optional_metrics_failure_is_degraded():
    snapshot = create_worker_readiness_service(healthy_checks(metrics=False)).evaluate()

    assert snapshot.status is TelegramOperationalStatus.DEGRADED

    assert snapshot.ready is True


@pytest.mark.parametrize(
    "dependency",
    [
        "configuration",
        "database",
        "job_repository",
        "receipt_repository",
        "keyring",
        "processor",
    ],
)
def test_required_dependency_failure_is_unready(
    dependency,
):
    values = {
        "configuration": lambda: True,
        "database": lambda: True,
        "job_repository": lambda: True,
        "receipt_repository": lambda: True,
        "keyring": lambda: True,
        "processor": lambda: True,
        "metrics_runtime": lambda: True,
    }

    values[dependency] = lambda: False

    snapshot = create_worker_readiness_service(
        TelegramWorkerReadinessChecks(**values)
    ).evaluate()

    assert snapshot.status is TelegramOperationalStatus.UNREADY

    assert snapshot.ready is False


def test_dependency_exception_is_fail_safe():
    def broken():
        raise RuntimeError("postgresql://user:password@private")

    checks = healthy_checks()

    snapshot = create_worker_readiness_service(
        TelegramWorkerReadinessChecks(
            configuration=(checks.configuration),
            database=broken,
            job_repository=(checks.job_repository),
            receipt_repository=(checks.receipt_repository),
            keyring=checks.keyring,
            processor=checks.processor,
            metrics_runtime=(checks.metrics_runtime),
        )
    ).evaluate()

    payload = repr(snapshot.to_safe_dict())

    assert snapshot.status is TelegramOperationalStatus.UNREADY

    assert "password" not in payload

    assert "postgresql://" not in payload


def test_factory_check_reports_type_only():
    check = create_factory_readiness_check(
        lambda: FakeKeyring(active_key_id="private-key-id"),
        detail_name="implementation",
    )

    result = check()

    assert result == {
        "passed": True,
        "implementation": "FakeKeyring",
    }

    assert "private-key-id" not in repr(result)


def test_factory_check_fails_on_none():
    check = create_factory_readiness_check(
        lambda: None,
        detail_name="implementation",
    )

    assert check() == {
        "passed": False,
        "implementation": "unavailable",
    }


def test_attribute_check_passes():
    check = create_attribute_readiness_check(
        lambda: FakeKeyring(active_key_id="key-v1"),
        attribute="active_key_id",
        expected_type=str,
    )

    result = check()

    assert result["passed"] is True

    assert "key-v1" not in repr(result)


def test_attribute_check_rejects_wrong_type():
    check = create_attribute_readiness_check(
        lambda: FakeKeyring(active_key_id=123),
        attribute="active_key_id",
        expected_type=str,
    )

    assert check()["passed"] is False


def test_callable_attribute_check():
    check = create_callable_attribute_check(
        lambda: FakeRepository(),
        attribute="find_by_update_id",
    )

    assert check() == {
        "passed": True,
        "attribute": "find_by_update_id",
        "callable": True,
    }


def test_database_select_check_executes_only_select():
    cursor = FakeCursor()

    connection = FakeConnection(cursor)

    check = create_database_select_check(lambda: connection)

    result = check()

    assert result["passed"] is True

    assert cursor.executed == ["SELECT 1"]

    assert cursor.closed is True
    assert connection.closed is True


def test_database_select_check_accepts_scalar():
    cursor = FakeCursor(row=1)

    check = create_database_select_check(lambda: FakeConnection(cursor))

    assert check()["passed"] is True


def test_database_select_check_failure_closes_resources():
    cursor = FakeCursor(fail=True)

    connection = FakeConnection(cursor)

    check = create_database_select_check(lambda: connection)

    with pytest.raises(RuntimeError):
        check()

    assert cursor.closed is True
    assert connection.closed is True


def test_database_select_check_has_no_write_statement():
    cursor = FakeCursor()

    check = create_database_select_check(lambda: FakeConnection(cursor))

    check()

    rendered = " ".join(cursor.executed).upper()

    forbidden = (
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "DROP",
        "ALTER",
        "TRUNCATE",
    )

    assert not any(statement in rendered for statement in forbidden)


@pytest.mark.parametrize(
    "factory",
    [
        lambda: create_factory_readiness_check(
            lambda: object(),
            detail_name="",
        ),
        lambda: create_attribute_readiness_check(
            lambda: object(),
            attribute="",
        ),
        lambda: create_callable_attribute_check(
            lambda: object(),
            attribute="",
        ),
    ],
)
def test_helper_requires_valid_name(
    factory,
):
    with pytest.raises(ValueError):
        factory()


def test_metrics_probe_can_be_omitted():
    checks = healthy_checks()

    snapshot = create_worker_readiness_service(
        TelegramWorkerReadinessChecks(
            configuration=(checks.configuration),
            database=checks.database,
            job_repository=(checks.job_repository),
            receipt_repository=(checks.receipt_repository),
            keyring=checks.keyring,
            processor=checks.processor,
            metrics_runtime=None,
        )
    ).evaluate()

    assert snapshot.status is TelegramOperationalStatus.HEALTHY

    assert len(snapshot.checks) == 6
