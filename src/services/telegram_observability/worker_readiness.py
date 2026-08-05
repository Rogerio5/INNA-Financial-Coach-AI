from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from .health_readiness import (
    TelegramOperationalStatusService,
)
from .readiness_probes import (
    ReadinessCheck,
    TelegramWorkerReadinessChecks,
    create_attribute_readiness_check,
    create_callable_attribute_check,
    create_database_select_check,
    create_factory_readiness_check,
    create_worker_readiness_service,
)


ObjectFactory = Callable[
    [],
    object,
]


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramWorkerReadinessDependencies:
    configuration_check: ReadinessCheck
    database_connection_factory: ObjectFactory
    job_repository_factory: ObjectFactory
    receipt_repository_factory: ObjectFactory
    keyring_factory: ObjectFactory
    processor_factory: ObjectFactory
    metrics_runtime_factory: ObjectFactory | None = None


def create_configuration_environment_check(
    *,
    required_values: Mapping[
        str,
        str | None,
    ],
) -> ReadinessCheck:
    normalized_names = tuple(
        sorted(str(name).strip() for name in required_values if str(name).strip())
    )

    def check() -> Mapping[str, object]:
        missing = tuple(
            name
            for name in normalized_names
            if not str(required_values.get(name) or "").strip()
        )

        return {
            "passed": not missing,
            "required_count": len(normalized_names),
            "missing_count": len(missing),
        }

    return check


def create_job_repository_contract_check(
    factory: ObjectFactory,
) -> ReadinessCheck:
    """
    Verifica somente a existência de um contrato
    público conhecido.

    O método não é executado.
    """

    return create_callable_attribute_check(
        factory,
        attribute=("claim_next_telegram_update_job"),
    )


def create_receipt_repository_contract_check(
    factory: ObjectFactory,
) -> ReadinessCheck:
    """
    Verifica somente a existência do contrato.

    Nenhum claim é executado.
    """

    return create_callable_attribute_check(
        factory,
        attribute=("claim_telegram_update"),
    )


def create_keyring_contract_check(
    factory: ObjectFactory,
) -> ReadinessCheck:
    return create_attribute_readiness_check(
        factory,
        attribute="active_key_id",
        expected_type=str,
    )


def create_processor_contract_check(
    factory: ObjectFactory,
) -> ReadinessCheck:
    def check() -> Mapping[str, object]:
        processor = factory()

        return {
            "passed": callable(processor),
            "callable": callable(processor),
            "implementation": (
                type(processor).__name__ if processor is not None else "unavailable"
            ),
        }

    return check


def create_metrics_runtime_contract_check(
    factory: ObjectFactory,
) -> ReadinessCheck:
    return create_factory_readiness_check(
        factory,
        detail_name="implementation",
    )


def create_productive_worker_readiness_service(
    dependencies: (TelegramWorkerReadinessDependencies),
) -> TelegramOperationalStatusService:
    metrics_check = None

    if dependencies.metrics_runtime_factory is not None:
        metrics_check = create_metrics_runtime_contract_check(
            dependencies.metrics_runtime_factory
        )

    checks = TelegramWorkerReadinessChecks(
        configuration=(dependencies.configuration_check),
        database=(
            create_database_select_check(dependencies.database_connection_factory)
        ),
        job_repository=(
            create_job_repository_contract_check(dependencies.job_repository_factory)
        ),
        receipt_repository=(
            create_receipt_repository_contract_check(
                dependencies.receipt_repository_factory
            )
        ),
        keyring=(create_keyring_contract_check(dependencies.keyring_factory)),
        processor=(create_processor_contract_check(dependencies.processor_factory)),
        metrics_runtime=metrics_check,
    )

    return create_worker_readiness_service(checks)


__all__ = [
    "ObjectFactory",
    "TelegramWorkerReadinessDependencies",
    "create_configuration_environment_check",
    "create_job_repository_contract_check",
    "create_keyring_contract_check",
    "create_metrics_runtime_contract_check",
    "create_processor_contract_check",
    "create_productive_worker_readiness_service",
    "create_receipt_repository_contract_check",
]
