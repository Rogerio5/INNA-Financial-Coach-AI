from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
import inspect
import math
import re
import time
from threading import Event
from typing import Any, Literal

from . import execution as execution_module
from . import repository as repository_module
from . import worker as worker_module


RunnerDecision = Literal[
    "idle",
    "completed",
    "retry_scheduled",
    "dead_lettered",
    "ownership_lost",
    "unavailable",
    "consistency_error",
]

RunnerStage = Literal[
    "idle",
    "claim",
    "decrypt",
    "process",
    "complete",
    "failure",
    "recovery",
]


RUNNER_ERROR_CODE_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,63}$")


class TelegramUpdateRunnerError(RuntimeError):
    """
    Erro sanitizado do runner Telegram.
    """


class TelegramUpdateRunnerConfigurationError(TelegramUpdateRunnerError):
    """
    Configuração inválida do worker.
    """


class TelegramUpdateProcessorError(TelegramUpdateRunnerError):
    """
    Erro conhecido e sanitizado do processador.
    """

    def __init__(
        self,
        error_code: str,
    ) -> None:
        normalized = _validate_error_code(error_code)

        self.error_code = normalized

        super().__init__("O processador Telegram não concluiu o update.")


class TelegramUpdateTransientProcessingError(TelegramUpdateProcessorError):
    """
    Erro que permite nova tentativa.
    """


class TelegramUpdatePermanentProcessingError(TelegramUpdateProcessorError):
    """
    Erro que deve ir diretamente a dead-letter.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateWorkerConfig:
    lease_seconds: int = 120

    idle_sleep_seconds: float = 1.0

    unavailable_sleep_seconds: float = 5.0

    recovery_interval_seconds: float = 30.0

    recovery_batch_size: int = 100

    retry_base_delay_seconds: int = 5

    retry_max_delay_seconds: int = 3600

    def __post_init__(
        self,
    ) -> None:
        _validate_integer(
            self.lease_seconds,
            field_name="lease_seconds",
            minimum=(repository_module.MIN_LEASE_SECONDS),
            maximum=(repository_module.MAX_LEASE_SECONDS),
        )

        _validate_positive_float(
            self.idle_sleep_seconds,
            field_name=("idle_sleep_seconds"),
            minimum=0.01,
            maximum=60.0,
        )

        _validate_positive_float(
            self.unavailable_sleep_seconds,
            field_name=("unavailable_sleep_seconds"),
            minimum=0.1,
            maximum=300.0,
        )

        _validate_positive_float(
            self.recovery_interval_seconds,
            field_name=("recovery_interval_seconds"),
            minimum=1.0,
            maximum=3600.0,
        )

        _validate_integer(
            self.recovery_batch_size,
            field_name=("recovery_batch_size"),
            minimum=1,
            maximum=(repository_module.MAX_RECOVERY_BATCH),
        )

        base = _validate_integer(
            self.retry_base_delay_seconds,
            field_name=("retry_base_delay_seconds"),
            minimum=0,
            maximum=(repository_module.MAX_RETRY_DELAY_SECONDS),
        )

        maximum = _validate_integer(
            self.retry_max_delay_seconds,
            field_name=("retry_max_delay_seconds"),
            minimum=0,
            maximum=(repository_module.MAX_RETRY_DELAY_SECONDS),
        )

        if base > maximum:
            raise (
                TelegramUpdateRunnerConfigurationError(
                    "O atraso-base não pode superar o atraso máximo."
                )
            )


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateWorkerDependencies:
    claim: Callable[..., Any] = field(
        default=(worker_module.claim_next_authenticated_telegram_update_job_atomic)
    )

    decrypt: Callable[..., Any] = field(
        default=(execution_module.decrypt_authenticated_telegram_worker_lease)
    )

    complete: Callable[..., Any] = field(
        default=(worker_module.complete_authenticated_telegram_update_job_atomic)
    )

    fail: Callable[..., Any] = field(
        default=(
            worker_module.retry_or_dead_letter_authenticated_telegram_update_job_atomic
        )
    )

    recover: Callable[..., Any] = field(
        default=(
            worker_module.recover_expired_authenticated_telegram_update_jobs_atomic
        )
    )

    monotonic: Callable[[], float] = field(default=time.monotonic)

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "claim",
            "decrypt",
            "complete",
            "fail",
            "recover",
            "monotonic",
        ):
            if not callable(
                getattr(
                    self,
                    name,
                )
            ):
                raise (
                    TelegramUpdateRunnerConfigurationError(
                        f"Dependência {name} inválida."
                    )
                )


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateRunnerResult:
    decision: RunnerDecision
    stage: RunnerStage

    update_id: int | None = None

    job_attempt_count: int | None = None
    job_max_attempts: int | None = None

    job_status: str | None = None

    error_code: str | None = None

    idempotent_replay: bool = False

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "decision": self.decision,
            "stage": self.stage,
            "update_id": self.update_id,
            "job_attempt_count": (self.job_attempt_count),
            "job_max_attempts": (self.job_max_attempts),
            "job_status": self.job_status,
            "error_code": self.error_code,
            "idempotent_replay": (self.idempotent_replay),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateRunnerSummary:
    cycles: int

    completed: int
    retry_scheduled: int
    dead_lettered: int
    idle: int

    ownership_lost: int
    unavailable: int
    consistency_errors: int

    recovered_retry: int
    recovered_dead_letter: int

    duration_seconds: float

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "cycles": self.cycles,
            "completed": self.completed,
            "retry_scheduled": (self.retry_scheduled),
            "dead_lettered": (self.dead_lettered),
            "idle": self.idle,
            "ownership_lost": (self.ownership_lost),
            "unavailable": self.unavailable,
            "consistency_errors": (self.consistency_errors),
            "recovered_retry": (self.recovered_retry),
            "recovered_dead_letter": (self.recovered_dead_letter),
            "duration_seconds": (self.duration_seconds),
        }


def _validate_integer(
    value: Any,
    *,
    field_name: str,
    minimum: int,
    maximum: int,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < minimum
        or value > maximum
    ):
        raise TelegramUpdateRunnerConfigurationError(f"{field_name} inválido.")

    return value


def _validate_positive_float(
    value: Any,
    *,
    field_name: str,
    minimum: float,
    maximum: float,
) -> float:
    if isinstance(value, bool) or not isinstance(
        value,
        (
            int,
            float,
        ),
    ):
        raise TelegramUpdateRunnerConfigurationError(f"{field_name} inválido.")

    normalized = float(value)

    if not math.isfinite(normalized) or normalized < minimum or normalized > maximum:
        raise TelegramUpdateRunnerConfigurationError(f"{field_name} inválido.")

    return normalized


def _validate_error_code(
    value: Any,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise TelegramUpdateRunnerConfigurationError("error_code inválido.")

    normalized = value.strip()

    if normalized != value or RUNNER_ERROR_CODE_PATTERN.fullmatch(normalized) is None:
        raise TelegramUpdateRunnerConfigurationError("error_code inválido.")

    return normalized


def calculate_worker_retry_delay_seconds(
    *,
    attempt_count: int,
    config: TelegramUpdateWorkerConfig,
) -> int:
    """
    Backoff exponencial determinístico e limitado.

    tentativa 1: base
    tentativa 2: base * 2
    tentativa 3: base * 4
    """
    normalized_attempt = _validate_integer(
        attempt_count,
        field_name="attempt_count",
        minimum=1,
        maximum=20,
    )

    raw_delay = config.retry_base_delay_seconds * (2 ** (normalized_attempt - 1))

    return min(
        raw_delay,
        config.retry_max_delay_seconds,
        repository_module.MAX_RETRY_DELAY_SECONDS,
    )


def _result_for_lease(
    *,
    lease: Any,
    decision: RunnerDecision,
    stage: RunnerStage,
    job_status: str | None = None,
    error_code: str | None = None,
    idempotent_replay: bool = False,
) -> TelegramUpdateRunnerResult:
    return TelegramUpdateRunnerResult(
        decision=decision,
        stage=stage,
        update_id=lease.update_id,
        job_attempt_count=(lease.job_attempt_count),
        job_max_attempts=(lease.job_max_attempts),
        job_status=job_status,
        error_code=error_code,
        idempotent_replay=(idempotent_replay),
    )


def _finalize_failure(
    *,
    lease: Any,
    dependencies: TelegramUpdateWorkerDependencies,
    config: TelegramUpdateWorkerConfig,
    error_code: str,
    force_dead_letter: bool,
) -> TelegramUpdateRunnerResult:
    normalized_error = _validate_error_code(error_code)

    retry_delay = (
        0
        if force_dead_letter
        else calculate_worker_retry_delay_seconds(
            attempt_count=(lease.job_attempt_count),
            config=config,
        )
    )

    try:
        outcome = dependencies.fail(
            lease,
            error_code=normalized_error,
            retry_delay_seconds=(retry_delay),
            force_dead_letter=(force_dead_letter),
        )

    except worker_module.TelegramUpdateWorkerOwnershipError:
        return _result_for_lease(
            lease=lease,
            decision="ownership_lost",
            stage="failure",
            error_code=normalized_error,
        )

    except worker_module.TelegramUpdateWorkerUnavailableError:
        return _result_for_lease(
            lease=lease,
            decision="unavailable",
            stage="failure",
            error_code=normalized_error,
        )

    except (
        worker_module.TelegramUpdateWorkerConsistencyError,
        worker_module.TelegramUpdateWorkerValidationError,
    ):
        return _result_for_lease(
            lease=lease,
            decision="consistency_error",
            stage="failure",
            error_code=normalized_error,
        )

    except Exception:
        return _result_for_lease(
            lease=lease,
            decision="unavailable",
            stage="failure",
            error_code=normalized_error,
        )

    status = getattr(
        outcome,
        "job_status",
        None,
    )

    replay = bool(
        getattr(
            outcome,
            "idempotent_replay",
            False,
        )
    )

    if status == "queued":
        return _result_for_lease(
            lease=lease,
            decision="retry_scheduled",
            stage="failure",
            job_status="queued",
            error_code=normalized_error,
            idempotent_replay=replay,
        )

    if status == "dead_letter":
        return _result_for_lease(
            lease=lease,
            decision="dead_lettered",
            stage="failure",
            job_status="dead_letter",
            error_code=normalized_error,
            idempotent_replay=replay,
        )

    return _result_for_lease(
        lease=lease,
        decision="consistency_error",
        stage="failure",
        error_code=normalized_error,
    )


def run_one_telegram_update_job(
    processor: Callable[
        [dict[str, Any]],
        Any,
    ],
    *,
    config: TelegramUpdateWorkerConfig | None = None,
    dependencies: TelegramUpdateWorkerDependencies | None = None,
    keyring: Any = None,
) -> TelegramUpdateRunnerResult:
    """
    Executa no máximo um job.

    O processor recebe somente uma cópia mutável
    do payload descriptografado.

    Somente o valor booleano False representa
    falha retornada pelo processador. None é aceito
    como sucesso para compatibilidade com o canal
    Telegram atual.
    """
    if not callable(processor):
        raise TelegramUpdateRunnerConfigurationError("processor inválido.")

    resolved_config = config or TelegramUpdateWorkerConfig()

    resolved_dependencies = dependencies or TelegramUpdateWorkerDependencies()

    try:
        lease = resolved_dependencies.claim(
            lease_seconds=(resolved_config.lease_seconds)
        )

    except worker_module.TelegramUpdateWorkerUnavailableError:
        return TelegramUpdateRunnerResult(
            decision="unavailable",
            stage="claim",
            error_code=("telegram.claim_unavailable"),
        )

    except (
        worker_module.TelegramUpdateWorkerConsistencyError,
        worker_module.TelegramUpdateWorkerValidationError,
    ):
        return TelegramUpdateRunnerResult(
            decision="consistency_error",
            stage="claim",
            error_code=("telegram.claim_inconsistent"),
        )

    except Exception:
        return TelegramUpdateRunnerResult(
            decision="unavailable",
            stage="claim",
            error_code=("telegram.claim_unavailable"),
        )

    if lease is None:
        return TelegramUpdateRunnerResult(
            decision="idle",
            stage="idle",
        )

    try:
        protected_payload = resolved_dependencies.decrypt(
            lease,
            keyring=keyring,
        )

    except execution_module.TelegramUpdateExecutionConfigurationError:
        return _finalize_failure(
            lease=lease,
            dependencies=(resolved_dependencies),
            config=resolved_config,
            error_code=("telegram.keyring_unavailable"),
            force_dead_letter=False,
        )

    except (
        execution_module.TelegramUpdateExecutionDecryptionError,
        execution_module.TelegramUpdateExecutionPayloadError,
    ):
        return _finalize_failure(
            lease=lease,
            dependencies=(resolved_dependencies),
            config=resolved_config,
            error_code=("telegram.payload_invalid"),
            force_dead_letter=True,
        )

    except execution_module.TelegramUpdateExecutionValidationError:
        return _result_for_lease(
            lease=lease,
            decision="consistency_error",
            stage="decrypt",
            error_code=("telegram.lease_invalid"),
        )

    except Exception:
        return _finalize_failure(
            lease=lease,
            dependencies=(resolved_dependencies),
            config=resolved_config,
            error_code=("telegram.decrypt_failed"),
            force_dead_letter=False,
        )

    try:
        update = protected_payload.to_processing_dict()

    except Exception:
        return _finalize_failure(
            lease=lease,
            dependencies=(resolved_dependencies),
            config=resolved_config,
            error_code=("telegram.payload_invalid"),
            force_dead_letter=True,
        )

    try:
        processing_result = processor(update)

        if inspect.isawaitable(processing_result):
            close = getattr(
                processing_result,
                "close",
                None,
            )

            if callable(close):
                close()

            return _finalize_failure(
                lease=lease,
                dependencies=(resolved_dependencies),
                config=resolved_config,
                error_code=("telegram.async_processor_unsupported"),
                force_dead_letter=True,
            )

    except TelegramUpdatePermanentProcessingError as error:
        return _finalize_failure(
            lease=lease,
            dependencies=(resolved_dependencies),
            config=resolved_config,
            error_code=error.error_code,
            force_dead_letter=True,
        )

    except TelegramUpdateTransientProcessingError as error:
        return _finalize_failure(
            lease=lease,
            dependencies=(resolved_dependencies),
            config=resolved_config,
            error_code=error.error_code,
            force_dead_letter=False,
        )

    except Exception:
        return _finalize_failure(
            lease=lease,
            dependencies=(resolved_dependencies),
            config=resolved_config,
            error_code=("telegram.processing_failed"),
            force_dead_letter=False,
        )

    finally:
        update = None

    if processing_result is False:
        return _finalize_failure(
            lease=lease,
            dependencies=(resolved_dependencies),
            config=resolved_config,
            error_code=("telegram.processing_failed"),
            force_dead_letter=False,
        )

    try:
        outcome = resolved_dependencies.complete(lease)

    except worker_module.TelegramUpdateWorkerOwnershipError:
        return _result_for_lease(
            lease=lease,
            decision="ownership_lost",
            stage="complete",
            error_code=("telegram.completion_ownership_lost"),
        )

    except worker_module.TelegramUpdateWorkerUnavailableError:
        return _result_for_lease(
            lease=lease,
            decision="unavailable",
            stage="complete",
            error_code=("telegram.completion_unavailable"),
        )

    except (
        worker_module.TelegramUpdateWorkerConsistencyError,
        worker_module.TelegramUpdateWorkerValidationError,
    ):
        return _result_for_lease(
            lease=lease,
            decision="consistency_error",
            stage="complete",
            error_code=("telegram.completion_inconsistent"),
        )

    except Exception:
        return _result_for_lease(
            lease=lease,
            decision="unavailable",
            stage="complete",
            error_code=("telegram.completion_unavailable"),
        )

    if (
        getattr(
            outcome,
            "job_status",
            None,
        )
        != "completed"
    ):
        return _result_for_lease(
            lease=lease,
            decision="consistency_error",
            stage="complete",
            error_code=("telegram.completion_inconsistent"),
        )

    return _result_for_lease(
        lease=lease,
        decision="completed",
        stage="complete",
        job_status="completed",
        idempotent_replay=bool(
            getattr(
                outcome,
                "idempotent_replay",
                False,
            )
        ),
    )


def _notify_safely(
    callback: Callable[
        [TelegramUpdateRunnerResult],
        Any,
    ]
    | None,
    result: TelegramUpdateRunnerResult,
) -> None:
    if callback is None:
        return

    try:
        callback(result)

    except Exception:
        return


def run_telegram_update_worker(
    processor: Callable[
        [dict[str, Any]],
        Any,
    ],
    *,
    stop_event: Any | None = None,
    config: TelegramUpdateWorkerConfig | None = None,
    dependencies: TelegramUpdateWorkerDependencies | None = None,
    keyring: Any = None,
    on_result: Callable[
        [TelegramUpdateRunnerResult],
        Any,
    ]
    | None = None,
    max_cycles: int | None = None,
) -> TelegramUpdateRunnerSummary:
    """
    Executa o worker até stop_event ser acionado.

    max_cycles existe para testes, smoke tests e
    execução controlada; None representa loop
    contínuo de produção.
    """
    if not callable(processor):
        raise TelegramUpdateRunnerConfigurationError("processor inválido.")

    if max_cycles is not None:
        _validate_integer(
            max_cycles,
            field_name="max_cycles",
            minimum=1,
            maximum=1_000_000,
        )

    resolved_config = config or TelegramUpdateWorkerConfig()

    resolved_dependencies = dependencies or TelegramUpdateWorkerDependencies()

    resolved_stop_event = stop_event if stop_event is not None else Event()

    if not callable(
        getattr(
            resolved_stop_event,
            "is_set",
            None,
        )
    ) or not callable(
        getattr(
            resolved_stop_event,
            "wait",
            None,
        )
    ):
        raise TelegramUpdateRunnerConfigurationError("stop_event inválido.")

    started_at = resolved_dependencies.monotonic()

    next_recovery_at = started_at

    counters = {
        "cycles": 0,
        "completed": 0,
        "retry_scheduled": 0,
        "dead_lettered": 0,
        "idle": 0,
        "ownership_lost": 0,
        "unavailable": 0,
        "consistency_errors": 0,
        "recovered_retry": 0,
        "recovered_dead_letter": 0,
    }

    while not resolved_stop_event.is_set():
        if max_cycles is not None and counters["cycles"] >= max_cycles:
            break

        counters["cycles"] += 1

        now = resolved_dependencies.monotonic()

        if now >= next_recovery_at:
            try:
                recovery = resolved_dependencies.recover(
                    limit=(resolved_config.recovery_batch_size)
                )

                counters["recovered_retry"] += int(
                    getattr(
                        recovery,
                        "retried",
                        0,
                    )
                )

                counters["recovered_dead_letter"] += int(
                    getattr(
                        recovery,
                        "dead_lettered",
                        0,
                    )
                )

            except Exception:
                counters["unavailable"] += 1

                recovery_result = TelegramUpdateRunnerResult(
                    decision="unavailable",
                    stage="recovery",
                    error_code=("telegram.recovery_unavailable"),
                )

                _notify_safely(
                    on_result,
                    recovery_result,
                )

                next_recovery_at = now + resolved_config.recovery_interval_seconds

                if resolved_stop_event.wait(resolved_config.unavailable_sleep_seconds):
                    break

                continue

            next_recovery_at = now + resolved_config.recovery_interval_seconds

        result = run_one_telegram_update_job(
            processor,
            config=resolved_config,
            dependencies=(resolved_dependencies),
            keyring=keyring,
        )

        _notify_safely(
            on_result,
            result,
        )

        if result.decision == "completed":
            counters["completed"] += 1

        elif result.decision == "retry_scheduled":
            counters["retry_scheduled"] += 1

        elif result.decision == "dead_lettered":
            counters["dead_lettered"] += 1

        elif result.decision == "idle":
            counters["idle"] += 1

        elif result.decision == "ownership_lost":
            counters["ownership_lost"] += 1

        elif result.decision == "unavailable":
            counters["unavailable"] += 1

        elif result.decision == "consistency_error":
            counters["consistency_errors"] += 1

        if result.decision == "idle":
            if resolved_stop_event.wait(resolved_config.idle_sleep_seconds):
                break

        elif result.decision in {
            "unavailable",
            "consistency_error",
        }:
            if resolved_stop_event.wait(resolved_config.unavailable_sleep_seconds):
                break

    finished_at = resolved_dependencies.monotonic()

    duration = max(
        0.0,
        finished_at - started_at,
    )

    return TelegramUpdateRunnerSummary(
        cycles=counters["cycles"],
        completed=counters["completed"],
        retry_scheduled=(counters["retry_scheduled"]),
        dead_lettered=(counters["dead_lettered"]),
        idle=counters["idle"],
        ownership_lost=(counters["ownership_lost"]),
        unavailable=(counters["unavailable"]),
        consistency_errors=(counters["consistency_errors"]),
        recovered_retry=(counters["recovered_retry"]),
        recovered_dead_letter=(counters["recovered_dead_letter"]),
        duration_seconds=round(
            duration,
            6,
        ),
    )


__all__ = [
    "RUNNER_ERROR_CODE_PATTERN",
    "TelegramUpdatePermanentProcessingError",
    "TelegramUpdateProcessorError",
    "TelegramUpdateRunnerConfigurationError",
    "TelegramUpdateRunnerError",
    "TelegramUpdateRunnerResult",
    "TelegramUpdateRunnerSummary",
    "TelegramUpdateTransientProcessingError",
    "TelegramUpdateWorkerConfig",
    "TelegramUpdateWorkerDependencies",
    "calculate_worker_retry_delay_seconds",
    "run_one_telegram_update_job",
    "run_telegram_update_worker",
]
