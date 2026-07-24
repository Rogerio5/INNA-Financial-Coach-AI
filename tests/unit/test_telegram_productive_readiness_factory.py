from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from types import ModuleType

import pytest

from src.services.telegram_observability import (
    TelegramOperationalStatus,
    create_productive_telegram_worker_readiness_service,
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

    def execute(
        self,
        statement,
    ):
        if self.fail:
            raise RuntimeError(
                "postgresql://user:password@private"
            )

        self.executed.append(
            statement
        )

    def fetchone(
        self,
    ):
        return self.row


@dataclass
class FakeConfiguration:
    lease_seconds: int = 120


class FakeKeyring:
    active_key_id = "private-key-id"

    def get_key(
        self,
        key_id,
    ):
        raise AssertionError(
            "get_key não deve ser chamado."
        )


def fake_processor(
    update,
):
    return update


class FakeMetricsRuntime:
    pass


def module_with_functions(
    name,
    function_names,
):
    module = ModuleType(
        name
    )

    for function_name in (
        function_names
    ):
        def forbidden(
            *args,
            _function_name=(
                function_name
            ),
            **kwargs,
        ):
            raise AssertionError(
                "Função mutante não deve "
                f"ser chamada: {_function_name}"
            )

        setattr(
            module,
            function_name,
            forbidden,
        )

    return module


JOB_FUNCTIONS = (
    "claim_next_telegram_update_job",
    "renew_telegram_update_job_lease",
    "complete_telegram_update_job",
    (
        "retry_or_dead_letter_"
        "telegram_update_job"
    ),
    (
        "recover_expired_"
        "telegram_update_jobs"
    ),
)

RECEIPT_FUNCTIONS = (
    "claim_telegram_update",
    "complete_telegram_update",
    "fail_telegram_update",
)


def build_service(
    *,
    row=(1,),
    database_fail=False,
    configuration_factory=(
        FakeConfiguration
    ),
    keyring_factory=FakeKeyring,
    processor_factory=(
        lambda: fake_processor
    ),
    metrics_factory=(
        FakeMetricsRuntime
    ),
    job_module=None,
    receipt_module=None,
):
    cursor = FakeCursor(
        row=row,
        fail=database_fail,
    )

    @contextmanager
    def cursor_context():
        yield cursor

    if job_module is None:
        job_module = (
            module_with_functions(
                "fake_jobs",
                JOB_FUNCTIONS,
            )
        )

    if receipt_module is None:
        receipt_module = (
            module_with_functions(
                "fake_receipts",
                RECEIPT_FUNCTIONS,
            )
        )

    service = (
        create_productive_telegram_worker_readiness_service(
            configuration_factory=(
                configuration_factory
            ),
            database_cursor_context_factory=(
                cursor_context
            ),
            job_repository_module_supplier=(
                lambda: job_module
            ),
            receipt_repository_module_supplier=(
                lambda: receipt_module
            ),
            keyring_factory=(
                keyring_factory
            ),
            processor_factory=(
                processor_factory
            ),
            metrics_runtime_factory=(
                metrics_factory
            ),
        )
    )

    return service, cursor


def test_productive_readiness_is_healthy():
    service, cursor = (
        build_service()
    )

    snapshot = service.evaluate()

    assert (
        snapshot.status
        is TelegramOperationalStatus.HEALTHY
    )

    assert snapshot.ready is True

    assert (
        cursor.executed
        == ["SELECT 1"]
    )

    assert len(
        snapshot.checks
    ) == 7


def test_repository_functions_are_not_called():
    service, _ = build_service()

    snapshot = service.evaluate()

    assert (
        snapshot.status
        is TelegramOperationalStatus.HEALTHY
    )


def test_database_failure_is_unready_and_safe():
    service, _ = build_service(
        database_fail=True
    )

    snapshot = service.evaluate()

    rendered = repr(
        snapshot.to_safe_dict()
    )

    assert (
        snapshot.status
        is TelegramOperationalStatus.UNREADY
    )

    assert "password" not in rendered
    assert "postgresql://" not in rendered


def test_invalid_database_row_is_unready():
    service, _ = build_service(
        row=(0,)
    )

    snapshot = service.evaluate()

    assert (
        snapshot.status
        is TelegramOperationalStatus.UNREADY
    )


def test_missing_job_contract_is_unready():
    job_module = ModuleType(
        "incomplete_jobs"
    )

    service, _ = build_service(
        job_module=job_module
    )

    snapshot = service.evaluate()

    assert (
        snapshot.status
        is TelegramOperationalStatus.UNREADY
    )


def test_missing_receipt_contract_is_unready():
    receipt_module = ModuleType(
        "incomplete_receipts"
    )

    service, _ = build_service(
        receipt_module=receipt_module
    )

    snapshot = service.evaluate()

    assert (
        snapshot.status
        is TelegramOperationalStatus.UNREADY
    )


def test_invalid_keyring_is_unready():
    service, _ = build_service(
        keyring_factory=(
            lambda: object()
        )
    )

    snapshot = service.evaluate()

    assert (
        snapshot.status
        is TelegramOperationalStatus.UNREADY
    )


def test_keyring_identifier_is_not_exposed():
    service, _ = build_service()

    rendered = repr(
        service.evaluate()
        .to_safe_dict()
    )

    assert (
        "private-key-id"
        not in rendered
    )


def test_non_callable_processor_is_unready():
    service, _ = build_service(
        processor_factory=(
            lambda: object()
        )
    )

    snapshot = service.evaluate()

    assert (
        snapshot.status
        is TelegramOperationalStatus.UNREADY
    )


def test_metrics_failure_is_degraded():
    service, _ = build_service(
        metrics_factory=(
            lambda: None
        )
    )

    snapshot = service.evaluate()

    assert (
        snapshot.status
        is TelegramOperationalStatus.DEGRADED
    )

    assert snapshot.ready is True


def test_metrics_check_can_be_disabled():
    cursor = FakeCursor()

    @contextmanager
    def cursor_context():
        yield cursor

    service = (
        create_productive_telegram_worker_readiness_service(
            configuration_factory=(
                FakeConfiguration
            ),
            database_cursor_context_factory=(
                cursor_context
            ),
            job_repository_module_supplier=(
                lambda: module_with_functions(
                    "fake_jobs",
                    JOB_FUNCTIONS,
                )
            ),
            receipt_repository_module_supplier=(
                lambda: module_with_functions(
                    "fake_receipts",
                    RECEIPT_FUNCTIONS,
                )
            ),
            keyring_factory=(
                FakeKeyring
            ),
            processor_factory=(
                lambda: fake_processor
            ),
            metrics_runtime_factory=None,
        )
    )

    snapshot = service.evaluate()

    assert (
        snapshot.status
        is TelegramOperationalStatus.HEALTHY
    )

    assert len(
        snapshot.checks
    ) == 6


def test_configuration_exception_is_safe():
    def broken():
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN=private"
        )

    service, _ = build_service(
        configuration_factory=broken
    )

    snapshot = service.evaluate()

    rendered = repr(
        snapshot.to_safe_dict()
    )

    assert (
        snapshot.status
        is TelegramOperationalStatus.UNREADY
    )

    assert "private" not in rendered
    assert "TELEGRAM_BOT_TOKEN" not in rendered


def test_missing_configuration_is_unready():
    service, _ = build_service(
        configuration_factory=(
            lambda: None
        )
    )

    snapshot = service.evaluate()

    assert (
        snapshot.status
        is TelegramOperationalStatus.UNREADY
    )


def test_configuration_object_is_accepted():
    service, _ = build_service(
        configuration_factory=(
            lambda: object()
        )
    )

    snapshot = service.evaluate()

    assert (
        snapshot.status
        is TelegramOperationalStatus.HEALTHY
    )
