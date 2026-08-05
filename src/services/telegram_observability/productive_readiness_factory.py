from __future__ import annotations

from types import ModuleType
from typing import Callable, Mapping

from .health_readiness import (
    TelegramOperationalStatusService,
)
from .readiness_probes import (
    ReadinessCheck,
    TelegramWorkerReadinessChecks,
    create_context_cursor_select_check,
    create_worker_readiness_service,
)


def _module_callable_contract_check(
    module_supplier: Callable[
        [],
        ModuleType,
    ],
    *,
    required_names: tuple[
        str,
        ...,
    ],
) -> ReadinessCheck:
    normalized_names = tuple(
        sorted({str(name).strip() for name in required_names if str(name).strip()})
    )

    if not normalized_names:
        raise ValueError("Contrato sem funções obrigatórias.")

    def check() -> Mapping[str, object]:
        module = module_supplier()

        if not isinstance(
            module,
            ModuleType,
        ):
            return {
                "passed": False,
                "contract_count": len(normalized_names),
                "available_count": 0,
            }

        available_count = sum(
            1
            for name in normalized_names
            if callable(
                getattr(
                    module,
                    name,
                    None,
                )
            )
        )

        return {
            "passed": (available_count == len(normalized_names)),
            "contract_count": len(normalized_names),
            "available_count": (available_count),
        }

    return check


def _factory_type_check(
    factory: Callable[
        [],
        object,
    ],
    *,
    detail_name: str,
) -> ReadinessCheck:
    normalized_detail_name = str(detail_name).strip()

    if not normalized_detail_name:
        raise ValueError("Nome do detalhe obrigatório.")

    def check() -> Mapping[str, object]:
        value = factory()

        return {
            "passed": (value is not None),
            normalized_detail_name: (
                type(value).__name__ if value is not None else "unavailable"
            ),
        }

    return check


def _keyring_check(
    factory: Callable[
        [],
        object,
    ],
) -> ReadinessCheck:
    def check() -> Mapping[str, object]:
        keyring = factory()

        active_key_id = getattr(
            keyring,
            "active_key_id",
            None,
        )

        get_key = getattr(
            keyring,
            "get_key",
            None,
        )

        active_key_available = isinstance(
            active_key_id,
            str,
        ) and bool(active_key_id.strip())

        return {
            "passed": (active_key_available and callable(get_key)),
            "active_key_available": (active_key_available),
            "get_key_callable": callable(get_key),
        }

    return check


def _processor_check(
    factory: Callable[
        [],
        object,
    ],
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


def _load_configuration() -> object:
    from src.channels.telegram_update_worker import (
        load_worker_config_from_env,
    )

    return load_worker_config_from_env()


def _load_keyring() -> object:
    from src.services.telegram_update_jobs.service import (
        load_telegram_update_keyring_from_env,
    )

    return load_telegram_update_keyring_from_env()


def _load_processor() -> object:
    from src.channels.telegram_update_worker import (
        load_telegram_processor,
    )

    return load_telegram_processor()


def _load_metrics_runtime() -> object:
    from src.channels.telegram_update_worker import (
        create_production_telegram_metrics_runtime,
    )

    return create_production_telegram_metrics_runtime()


def _job_repository_module() -> ModuleType:
    from src.services.telegram_update_jobs import (
        repository,
    )

    return repository


def _receipt_repository_module() -> ModuleType:
    from src.services.telegram_update_receipts import (
        repository,
    )

    return repository


def _database_cursor_context() -> object:
    from src.database.connection import (
        cursor_postgres,
    )

    return cursor_postgres(
        dict_cursor=False,
        commit_automatico=False,
    )


def create_productive_telegram_worker_readiness_service(
    *,
    configuration_factory: Callable[
        [],
        object,
    ] = _load_configuration,
    database_cursor_context_factory: Callable[
        [],
        object,
    ] = _database_cursor_context,
    job_repository_module_supplier: Callable[
        [],
        ModuleType,
    ] = _job_repository_module,
    receipt_repository_module_supplier: Callable[
        [],
        ModuleType,
    ] = _receipt_repository_module,
    keyring_factory: Callable[
        [],
        object,
    ] = _load_keyring,
    processor_factory: Callable[
        [],
        object,
    ] = _load_processor,
    metrics_runtime_factory: (
        Callable[
            [],
            object,
        ]
        | None
    ) = _load_metrics_runtime,
) -> TelegramOperationalStatusService:
    configuration_check = _factory_type_check(
        configuration_factory,
        detail_name="implementation",
    )

    database_check = create_context_cursor_select_check(database_cursor_context_factory)

    job_repository_check = _module_callable_contract_check(
        job_repository_module_supplier,
        required_names=(
            ("claim_next_telegram_update_job"),
            ("renew_telegram_update_job_lease"),
            ("complete_telegram_update_job"),
            ("retry_or_dead_letter_telegram_update_job"),
            ("recover_expired_telegram_update_jobs"),
        ),
    )

    receipt_repository_check = _module_callable_contract_check(
        receipt_repository_module_supplier,
        required_names=(
            "claim_telegram_update",
            "complete_telegram_update",
            "fail_telegram_update",
        ),
    )

    metrics_check = None

    if metrics_runtime_factory is not None:
        metrics_check = _factory_type_check(
            metrics_runtime_factory,
            detail_name="implementation",
        )

    return create_worker_readiness_service(
        TelegramWorkerReadinessChecks(
            configuration=(configuration_check),
            database=database_check,
            job_repository=(job_repository_check),
            receipt_repository=(receipt_repository_check),
            keyring=(_keyring_check(keyring_factory)),
            processor=(_processor_check(processor_factory)),
            metrics_runtime=(metrics_check),
        )
    )


__all__ = [
    "create_productive_telegram_worker_readiness_service",
]
