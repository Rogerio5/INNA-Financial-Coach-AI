from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from .health_readiness import (
    CallableTelegramProbe,
    TelegramOperationalStatusService,
    TelegramProbe,
    TelegramProbeResult,
    TelegramProbeSeverity,
)


ReadinessCheckResult = (
    bool
    | Mapping[str, object]
    | TelegramProbeResult
)

ReadinessCheck = Callable[
    [],
    ReadinessCheckResult,
]


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramWorkerReadinessChecks:
    configuration: ReadinessCheck
    database: ReadinessCheck
    job_repository: ReadinessCheck
    receipt_repository: ReadinessCheck
    keyring: ReadinessCheck
    processor: ReadinessCheck
    metrics_runtime: ReadinessCheck | None = None


def _probe(
    *,
    name: str,
    severity: TelegramProbeSeverity | str,
    check: ReadinessCheck,
    error_category: str,
) -> CallableTelegramProbe:
    return CallableTelegramProbe(
        name=name,
        severity=severity,
        check=check,
        error_category=error_category,
    )


def create_configuration_readiness_probe(
    check: ReadinessCheck,
) -> TelegramProbe:
    return _probe(
        name="configuration",
        severity=TelegramProbeSeverity.REQUIRED,
        check=check,
        error_category="configuration",
    )


def create_database_readiness_probe(
    check: ReadinessCheck,
) -> TelegramProbe:
    return _probe(
        name="database",
        severity=TelegramProbeSeverity.REQUIRED,
        check=check,
        error_category="database",
    )


def create_job_repository_readiness_probe(
    check: ReadinessCheck,
) -> TelegramProbe:
    return _probe(
        name="job_repository",
        severity=TelegramProbeSeverity.REQUIRED,
        check=check,
        error_category="persistence",
    )


def create_receipt_repository_readiness_probe(
    check: ReadinessCheck,
) -> TelegramProbe:
    return _probe(
        name="receipt_repository",
        severity=TelegramProbeSeverity.REQUIRED,
        check=check,
        error_category="persistence",
    )


def create_keyring_readiness_probe(
    check: ReadinessCheck,
) -> TelegramProbe:
    return _probe(
        name="keyring",
        severity=TelegramProbeSeverity.REQUIRED,
        check=check,
        error_category="encryption",
    )


def create_processor_readiness_probe(
    check: ReadinessCheck,
) -> TelegramProbe:
    return _probe(
        name="processor",
        severity=TelegramProbeSeverity.REQUIRED,
        check=check,
        error_category="dependency",
    )


def create_metrics_runtime_readiness_probe(
    check: ReadinessCheck,
) -> TelegramProbe:
    return _probe(
        name="metrics_runtime",
        severity=TelegramProbeSeverity.OPTIONAL,
        check=check,
        error_category="internal",
    )


def create_factory_readiness_check(
    factory: Callable[[], object],
    *,
    detail_name: str,
) -> ReadinessCheck:
    normalized_detail_name = str(
        detail_name
    ).strip()

    if not normalized_detail_name:
        raise ValueError(
            "Nome do detalhe obrigatório."
        )

    def check() -> Mapping[str, object]:
        instance = factory()

        return {
            "passed": (
                instance is not None
            ),
            normalized_detail_name: (
                type(instance).__name__
                if instance is not None
                else "unavailable"
            ),
        }

    return check


def create_attribute_readiness_check(
    supplier: Callable[[], object],
    *,
    attribute: str,
    expected_type: (
        type
        | tuple[type, ...]
        | None
    ) = None,
) -> ReadinessCheck:
    normalized_attribute = str(
        attribute
    ).strip()

    if not normalized_attribute:
        raise ValueError(
            "Nome do atributo obrigatório."
        )

    def check() -> Mapping[str, object]:
        instance = supplier()

        if instance is None:
            return {
                "passed": False,
                "attribute": (
                    normalized_attribute
                ),
                "available": False,
            }

        value = getattr(
            instance,
            normalized_attribute,
            None,
        )

        available = (
            value is not None
        )

        if (
            available
            and expected_type is not None
        ):
            available = isinstance(
                value,
                expected_type,
            )

        return {
            "passed": available,
            "attribute": (
                normalized_attribute
            ),
            "available": available,
        }

    return check


def create_callable_attribute_check(
    supplier: Callable[[], object],
    *,
    attribute: str,
) -> ReadinessCheck:
    normalized_attribute = str(
        attribute
    ).strip()

    if not normalized_attribute:
        raise ValueError(
            "Nome do atributo obrigatório."
        )

    def check() -> Mapping[str, object]:
        instance = supplier()

        value = getattr(
            instance,
            normalized_attribute,
            None,
        )

        available = callable(
            value
        )

        return {
            "passed": available,
            "attribute": (
                normalized_attribute
            ),
            "callable": available,
        }

    return check


def create_database_select_check(
    connection_factory: Callable[
        [],
        object,
    ],
) -> ReadinessCheck:
    """
    Executa apenas SELECT 1.

    Não realiza commit, rollback explícito,
    criação de tabela ou escrita.
    """

    def check() -> Mapping[str, object]:
        connection = (
            connection_factory()
        )

        if connection is None:
            return {
                "passed": False,
                "driver": "unavailable",
            }

        cursor = None

        try:
            cursor_factory = getattr(
                connection,
                "cursor",
                None,
            )

            if not callable(
                cursor_factory
            ):
                return {
                    "passed": False,
                    "driver": (
                        type(connection)
                        .__name__
                    ),
                    "cursor": False,
                }

            cursor = cursor_factory()

            execute = getattr(
                cursor,
                "execute",
                None,
            )

            if not callable(
                execute
            ):
                return {
                    "passed": False,
                    "driver": (
                        type(connection)
                        .__name__
                    ),
                    "execute": False,
                }

            execute(
                "SELECT 1"
            )

            fetchone = getattr(
                cursor,
                "fetchone",
                None,
            )

            row = (
                fetchone()
                if callable(fetchone)
                else None
            )

            passed = (
                row is None
                or row == (1,)
                or row == [1]
                or row == 1
            )

            return {
                "passed": passed,
                "driver": (
                    type(connection)
                    .__name__
                ),
                "query": "select_1",
            }

        finally:
            if cursor is not None:
                close_cursor = getattr(
                    cursor,
                    "close",
                    None,
                )

                if callable(
                    close_cursor
                ):
                    close_cursor()

            close_connection = getattr(
                connection,
                "close",
                None,
            )

            if callable(
                close_connection
            ):
                close_connection()

    return check



def create_context_cursor_select_check(
    cursor_context_factory: Callable[
        [],
        object,
    ],
) -> ReadinessCheck:
    """
    Executa SELECT 1 usando um context manager
    que fornece diretamente o cursor.

    Nenhuma operação de escrita ou commit
    explícito é executada.
    """

    def check() -> Mapping[str, object]:
        context = (
            cursor_context_factory()
        )

        enter = getattr(
            context,
            "__enter__",
            None,
        )

        exit_method = getattr(
            context,
            "__exit__",
            None,
        )

        if (
            not callable(enter)
            or not callable(exit_method)
        ):
            return {
                "passed": False,
                "contract": (
                    "cursor_context"
                ),
                "context_manager": False,
            }

        with context as cursor:
            execute = getattr(
                cursor,
                "execute",
                None,
            )

            if not callable(
                execute
            ):
                return {
                    "passed": False,
                    "contract": (
                        "cursor_context"
                    ),
                    "execute": False,
                }

            execute(
                "SELECT 1"
            )

            fetchone = getattr(
                cursor,
                "fetchone",
                None,
            )

            row = (
                fetchone()
                if callable(fetchone)
                else None
            )

        passed = (
            row is None
            or row == (1,)
            or row == [1]
            or row == 1
        )

        return {
            "passed": passed,
            "query": "select_1",
            "contract": "cursor_context",
        }

    return check

def create_worker_readiness_service(
    checks: TelegramWorkerReadinessChecks,
) -> TelegramOperationalStatusService:
    probes: list[
        TelegramProbe
    ] = [
        create_configuration_readiness_probe(
            checks.configuration
        ),
        create_database_readiness_probe(
            checks.database
        ),
        create_job_repository_readiness_probe(
            checks.job_repository
        ),
        create_receipt_repository_readiness_probe(
            checks.receipt_repository
        ),
        create_keyring_readiness_probe(
            checks.keyring
        ),
        create_processor_readiness_probe(
            checks.processor
        ),
    ]

    if (
        checks.metrics_runtime
        is not None
    ):
        probes.append(
            create_metrics_runtime_readiness_probe(
                checks.metrics_runtime
            )
        )

    return TelegramOperationalStatusService(
        probes=tuple(
            probes
        )
    )


__all__ = [
    "ReadinessCheck",
    "ReadinessCheckResult",
    "TelegramWorkerReadinessChecks",
    "create_attribute_readiness_check",
    "create_callable_attribute_check",
    "create_configuration_readiness_probe",
    "create_context_cursor_select_check",
    "create_database_readiness_probe",
    "create_database_select_check",
    "create_factory_readiness_check",
    "create_job_repository_readiness_probe",
    "create_keyring_readiness_probe",
    "create_metrics_runtime_readiness_probe",
    "create_processor_readiness_probe",
    "create_receipt_repository_readiness_probe",
    "create_worker_readiness_service",
]
