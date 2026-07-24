from __future__ import annotations

import argparse
import inspect
import json
import logging
import math
import os
import signal
import sys
import time

from collections.abc import (
    Callable,
    Mapping,
    Sequence,
)
from threading import Event
from typing import Any, TextIO

from src.services.telegram_observability import (
    JsonTelegramOperationalEventSink,
    NoOpTelegramConversationMetrics,
    NoOpTelegramOperationalEventSink,
    TelegramConversationMetrics,
    TelegramOperationalEventSink,
    CompositeTelegramConversationMetrics,
    InMemoryTelegramProductiveMetrics,
    ProductiveTelegramConversationMetricsAdapter,
    SafeTelegramProductiveMetrics,
    SafeTelegramProductiveOperations,
    TelegramProductiveOperationsRecorder,
)

from src.services.telegram_update_jobs import (
    TelegramUpdateJobConfigurationError,
    TelegramUpdateRunnerConfigurationError,
    TelegramUpdateRunnerResult,
    TelegramUpdateRunnerSummary,
    TelegramUpdateWorkerConfig,
    load_telegram_update_keyring_from_env,
    run_telegram_update_worker,
)


EXIT_OK = 0
EXIT_RUNTIME_ERROR = 1
EXIT_CONFIGURATION_ERROR = 2
EXIT_INTERRUPTED = 130


ENV_LEASE_SECONDS = (
    "INNA_TELEGRAM_WORKER_LEASE_SECONDS"
)

ENV_IDLE_SLEEP_SECONDS = (
    "INNA_TELEGRAM_WORKER_IDLE_SLEEP_SECONDS"
)

ENV_UNAVAILABLE_SLEEP_SECONDS = (
    "INNA_TELEGRAM_WORKER_"
    "UNAVAILABLE_SLEEP_SECONDS"
)

ENV_RECOVERY_INTERVAL_SECONDS = (
    "INNA_TELEGRAM_WORKER_"
    "RECOVERY_INTERVAL_SECONDS"
)

ENV_RECOVERY_BATCH_SIZE = (
    "INNA_TELEGRAM_WORKER_"
    "RECOVERY_BATCH_SIZE"
)

ENV_RETRY_BASE_DELAY_SECONDS = (
    "INNA_TELEGRAM_WORKER_"
    "RETRY_BASE_DELAY_SECONDS"
)

ENV_RETRY_MAX_DELAY_SECONDS = (
    "INNA_TELEGRAM_WORKER_"
    "RETRY_MAX_DELAY_SECONDS"
)


def _configuration_error() -> (
    TelegramUpdateRunnerConfigurationError
):
    return TelegramUpdateRunnerConfigurationError(
        "A configuração do worker Telegram "
        "é inválida."
    )


def _read_integer(
    environment: Mapping[str, str],
    name: str,
    default: int,
) -> int:
    raw_value = environment.get(
        name
    )

    if raw_value is None:
        return default

    normalized = raw_value.strip()

    if not normalized:
        raise _configuration_error()

    try:
        value = int(
            normalized,
            10,
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        raise _configuration_error() from None

    return value


def _read_float(
    environment: Mapping[str, str],
    name: str,
    default: float,
) -> float:
    raw_value = environment.get(
        name
    )

    if raw_value is None:
        return default

    normalized = raw_value.strip()

    if not normalized:
        raise _configuration_error()

    try:
        value = float(
            normalized
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        raise _configuration_error() from None

    if not math.isfinite(
        value
    ):
        raise _configuration_error()

    return value


def load_worker_config_from_env(
    environment: Mapping[str, str]
        | None = None,
) -> TelegramUpdateWorkerConfig:
    """
    Carrega somente configurações operacionais.

    Segredos e chaves criptográficas são
    carregados pelo serviço de keyring.
    """
    resolved_environment = (
        environment
        if environment is not None
        else os.environ
    )

    defaults = (
        TelegramUpdateWorkerConfig()
    )

    try:
        return TelegramUpdateWorkerConfig(
            lease_seconds=_read_integer(
                resolved_environment,
                ENV_LEASE_SECONDS,
                defaults.lease_seconds,
            ),
            idle_sleep_seconds=_read_float(
                resolved_environment,
                ENV_IDLE_SLEEP_SECONDS,
                defaults.idle_sleep_seconds,
            ),
            unavailable_sleep_seconds=(
                _read_float(
                    resolved_environment,
                    ENV_UNAVAILABLE_SLEEP_SECONDS,
                    defaults
                    .unavailable_sleep_seconds,
                )
            ),
            recovery_interval_seconds=(
                _read_float(
                    resolved_environment,
                    ENV_RECOVERY_INTERVAL_SECONDS,
                    defaults
                    .recovery_interval_seconds,
                )
            ),
            recovery_batch_size=(
                _read_integer(
                    resolved_environment,
                    ENV_RECOVERY_BATCH_SIZE,
                    defaults
                    .recovery_batch_size,
                )
            ),
            retry_base_delay_seconds=(
                _read_integer(
                    resolved_environment,
                    ENV_RETRY_BASE_DELAY_SECONDS,
                    defaults
                    .retry_base_delay_seconds,
                )
            ),
            retry_max_delay_seconds=(
                _read_integer(
                    resolved_environment,
                    ENV_RETRY_MAX_DELAY_SECONDS,
                    defaults
                    .retry_max_delay_seconds,
                )
            ),
        )

    except TelegramUpdateRunnerConfigurationError:
        raise

    except Exception:
        raise _configuration_error() from None



def _observable_bridge_factory_kwargs(
    bridge_factory: Callable[..., Any],
    *,
    metrics: TelegramConversationMetrics,
    event_sink: TelegramOperationalEventSink,
    clock: Callable[[], float],
) -> dict[str, object]:
    """
    Retorna os argumentos de observabilidade suportados pela factory.

    Factories legadas e doubles de teste sem parâmetros recebem um
    dicionário vazio. A chamada produtiva da factory permanece dentro
    de load_telegram_processor.
    """
    try:
        signature = inspect.signature(
            bridge_factory
        )

    except (
        TypeError,
        ValueError,
    ):
        return {
            "metrics": metrics,
            "event_sink": event_sink,
            "clock": clock,
        }

    try:
        signature.bind(
            metrics=metrics,
            event_sink=event_sink,
            clock=clock,
        )

    except TypeError:
        return {}

    return {
        "metrics": metrics,
        "event_sink": event_sink,
        "clock": clock,
    }



_TELEGRAM_OPERATIONAL_LOGGER_NAME = (
    "inna.telegram.operations"
)

_TELEGRAM_OPERATIONAL_LOG_LEVEL_ENV = (
    "TELEGRAM_OPERATIONAL_LOG_LEVEL"
)

_DEFAULT_TELEGRAM_OPERATIONAL_LOG_LEVEL = (
    "INFO"
)

_MANAGED_TELEGRAM_LOG_HANDLER_ATTRIBUTE = (
    "_inna_telegram_structured_handler"
)

_ALLOWED_TELEGRAM_OPERATIONAL_LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def _resolve_telegram_operational_log_level(
    value: str | None,
) -> int:
    resolved = (
        value
        if value is not None
        else os.getenv(
            _TELEGRAM_OPERATIONAL_LOG_LEVEL_ENV,
            _DEFAULT_TELEGRAM_OPERATIONAL_LOG_LEVEL,
        )
    )

    normalized = str(
        resolved
    ).strip().upper()

    level = (
        _ALLOWED_TELEGRAM_OPERATIONAL_LOG_LEVELS.get(
            normalized
        )
    )

    if level is None:
        allowed = ", ".join(
            sorted(
                _ALLOWED_TELEGRAM_OPERATIONAL_LOG_LEVELS
            )
        )

        raise TelegramUpdateRunnerConfigurationError(
            "Nível de logging Telegram inválido. "
            f"Valores permitidos: {allowed}."
        )

    return level



class TelegramProductiveMetricsRuntime:
    """
    Mantém uma única instância do registry produtivo
    durante a vida do processo do worker.
    """

    def __init__(self) -> None:
        registry = (
            InMemoryTelegramProductiveMetrics()
        )

        self.registry = registry

        self.safe_registry = (
            SafeTelegramProductiveMetrics(
                registry
            )
        )

        self.adapter = (
            ProductiveTelegramConversationMetricsAdapter(
                self.safe_registry
            )
        )

        self.operations = (
            SafeTelegramProductiveOperations(
                TelegramProductiveOperationsRecorder(
                    self.safe_registry
                )
            )
        )


def create_production_telegram_metrics_runtime(
) -> TelegramProductiveMetricsRuntime:
    return TelegramProductiveMetricsRuntime()


def create_production_telegram_event_sink(
    *,
    stream: TextIO | None = None,
    level_name: str | None = None,
    logger: logging.Logger | None = None,
) -> TelegramOperationalEventSink:
    """
    Cria o sink JSON produtivo do Telegram.

    O logger usa um único handler gerenciado, não propaga
    para o root logger e escreve somente a mensagem JSON.
    """
    resolved_logger = (
        logger
        if logger is not None
        else logging.getLogger(
            _TELEGRAM_OPERATIONAL_LOGGER_NAME
        )
    )

    if not isinstance(
        resolved_logger,
        logging.Logger,
    ):
        raise TelegramUpdateRunnerConfigurationError(
            "Logger operacional Telegram inválido."
        )

    level = (
        _resolve_telegram_operational_log_level(
            level_name
        )
    )

    resolved_logger.setLevel(
        level
    )

    resolved_logger.propagate = False

    managed_handlers = [
        handler
        for handler in resolved_logger.handlers
        if bool(
            getattr(
                handler,
                _MANAGED_TELEGRAM_LOG_HANDLER_ATTRIBUTE,
                False,
            )
        )
    ]

    desired_stream = (
        stream
        if stream is not None
        else sys.stderr
    )

    matching_handler = next(
        (
            handler
            for handler in managed_handlers
            if getattr(
                handler,
                "stream",
                None,
            )
            is desired_stream
        ),
        None,
    )

    if matching_handler is None:
        for handler in managed_handlers:
            resolved_logger.removeHandler(
                handler
            )

            try:
                handler.close()
            except Exception:
                pass

        matching_handler = logging.StreamHandler(
            desired_stream
        )

        setattr(
            matching_handler,
            _MANAGED_TELEGRAM_LOG_HANDLER_ATTRIBUTE,
            True,
        )

        matching_handler.setFormatter(
            logging.Formatter(
                "%(message)s"
            )
        )

        resolved_logger.addHandler(
            matching_handler
        )

    matching_handler.setLevel(
        level
    )

    return JsonTelegramOperationalEventSink(
        logger=resolved_logger
    )


def load_telegram_processor(
    *,
    metrics_factory: Callable[
        [],
        TelegramConversationMetrics,
    ] = NoOpTelegramConversationMetrics,
    event_sink_factory: Callable[
        [],
        TelegramOperationalEventSink,
    ] = NoOpTelegramOperationalEventSink,
    clock: Callable[[], float] = (
        time.perf_counter
    ),
):
    """
    Compõe o processador produtivo do worker.

    Uma única bridge, um único coletor de métricas e um único event sink
    são criados durante a inicialização do processo e reutilizados por
    todos os jobs desta instância.

    O runtime PostgreSQL permanece lazy: a composição não abre conexão
    antecipadamente.
    """
    from api.telegram_webhook import (
        process_telegram_update,
    )
    from src.services.telegram_conversation_state import (
        create_postgres_telegram_webhook_conversation_bridge,
    )

    if not callable(
        process_telegram_update
    ):
        raise TelegramUpdateRunnerConfigurationError(
            "O processador Telegram é inválido."
        )

    if not callable(
        create_postgres_telegram_webhook_conversation_bridge
    ):
        raise TelegramUpdateRunnerConfigurationError(
            "A factory da conversation bridge é inválida."
        )

    if not callable(metrics_factory):
        raise TelegramUpdateRunnerConfigurationError(
            "A factory de métricas é inválida."
        )

    if not callable(event_sink_factory):
        raise TelegramUpdateRunnerConfigurationError(
            "A factory de eventos é inválida."
        )

    if not callable(clock):
        raise TelegramUpdateRunnerConfigurationError(
            "O relógio de observabilidade é inválido."
        )

    try:
        metrics = metrics_factory()
        event_sink = event_sink_factory()

        if not isinstance(
            metrics,
            TelegramConversationMetrics,
        ):
            raise TypeError(
                "Coletor de métricas inválido."
            )

        if not isinstance(
            event_sink,
            TelegramOperationalEventSink,
        ):
            raise TypeError(
                "Event sink inválido."
            )

        bridge_factory_kwargs = (
            _observable_bridge_factory_kwargs(
                create_postgres_telegram_webhook_conversation_bridge,
                metrics=metrics,
                event_sink=event_sink,
                clock=clock,
            )
        )

        conversation_bridge = (
            create_postgres_telegram_webhook_conversation_bridge(
                **bridge_factory_kwargs
            )
        )

    except Exception:
        raise TelegramUpdateRunnerConfigurationError(
            "Não foi possível compor o estado "
            "conversacional durável."
        ) from None

    if conversation_bridge is None:
        raise TelegramUpdateRunnerConfigurationError(
            "A conversation bridge criada é inválida."
        )

    def process_with_durable_conversation_state(
        update: dict,
    ):
        return process_telegram_update(
            update,
            conversation_bridge=conversation_bridge,
        )

    return process_with_durable_conversation_state



def _emit_event(
    event: str,
    payload: Mapping[str, object],
    *,
    stream: TextIO,
) -> None:
    record = {
        "event": event,
        "data": dict(
            payload
        ),
    }

    serialized = json.dumps(
        record,
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        allow_nan=False,
    )

    print(
        serialized,
        file=stream,
        flush=True,
    )


def emit_runner_result(
    result: TelegramUpdateRunnerResult,
    *,
    stream: TextIO,
) -> None:
    """
    Registra somente o contrato seguro do runner.

    Jobs idle são omitidos para evitar logs
    excessivos em produção.
    """
    if result.decision == "idle":
        return

    _emit_event(
        "telegram_worker_result",
        result.to_safe_dict(),
        stream=stream,
    )



def _productive_error_category_for_result(
    result: TelegramUpdateRunnerResult,
) -> str:
    error_code = str(
        getattr(
            result,
            "error_code",
            "",
        )
        or ""
    ).strip().lower()

    stage = str(
        getattr(
            result,
            "stage",
            "",
        )
        or ""
    ).strip().lower()

    if "timeout" in error_code:
        return "timeout"

    if (
        "ownership_lost" in error_code
        or "ownership" in error_code
    ):
        return "optimistic_conflict"

    if (
        "unavailable" in error_code
        or "unavailable" in stage
    ):
        return "dependency"

    if (
        "inconsistent" in error_code
        or "consistency" in error_code
    ):
        return "persistence"

    if (
        "decrypt" in error_code
        or "keyring" in error_code
        or "encryption" in error_code
    ):
        return "encryption"

    if (
        "validation" in error_code
        or "invalid" in error_code
    ):
        return "validation"

    if (
        "delivery" in error_code
        or "send" in error_code
    ):
        return "delivery"

    return "unknown"


def _productive_cycle_result_for_runner_result(
    result: TelegramUpdateRunnerResult,
) -> str:
    decision = str(
        getattr(
            result,
            "decision",
            "",
        )
        or ""
    ).strip().lower()

    stage = str(
        getattr(
            result,
            "stage",
            "",
        )
        or ""
    ).strip().lower()

    if decision == "idle":
        return "empty"

    if (
        stage == "recovery"
        and decision != "unavailable"
    ):
        return "processed"

    if decision in {
        "completed",
        "retry_scheduled",
        "dead_lettered",
    }:
        return "processed"

    if decision in {
        "ownership_lost",
        "unavailable",
        "consistency_error",
    }:
        return "failed"

    return "unknown"


def _productive_update_outcome_for_runner_result(
    result: TelegramUpdateRunnerResult,
) -> tuple[str, str | None] | None:
    decision = str(
        getattr(
            result,
            "decision",
            "",
        )
        or ""
    ).strip().lower()

    stage = str(
        getattr(
            result,
            "stage",
            "",
        )
        or ""
    ).strip().lower()

    idempotent_replay = bool(
        getattr(
            result,
            "idempotent_replay",
            False,
        )
    )

    if (
        decision == "idle"
        or stage == "recovery"
    ):
        return None

    if idempotent_replay:
        return (
            "duplicate",
            None,
        )

    if decision == "completed":
        return (
            "success",
            None,
        )

    if decision in {
        "retry_scheduled",
        "dead_lettered",
        "ownership_lost",
        "unavailable",
        "consistency_error",
    }:
        return (
            "error",
            _productive_error_category_for_result(
                result
            ),
        )

    return (
        "unknown",
        "unknown",
    )



def _productive_receipt_for_runner_result(
    result: TelegramUpdateRunnerResult,
) -> tuple[str, str, str | None] | None:
    decision = str(
        getattr(
            result,
            "decision",
            "",
        )
        or ""
    ).strip().lower()

    stage = str(
        getattr(
            result,
            "stage",
            "",
        )
        or ""
    ).strip().lower()

    if (
        decision == "idle"
        or stage == "recovery"
    ):
        return None

    idempotent_replay = bool(
        getattr(
            result,
            "idempotent_replay",
            False,
        )
    )

    error_category = (
        _productive_error_category_for_result(
            result
        )
    )

    if idempotent_replay:
        return (
            "duplicate",
            "duplicate",
            None,
        )

    if decision == "completed":
        return (
            "completed",
            "success",
            None,
        )

    if decision in {
        "retry_scheduled",
        "dead_lettered",
    }:
        return (
            "failed",
            "error",
            error_category,
        )

    if decision == "ownership_lost":
        return (
            "released",
            "conflict",
            "optimistic_conflict",
        )

    if stage == "claim":
        if decision == "consistency_error":
            return (
                "claimed",
                "conflict",
                "persistence",
            )

        return (
            "claimed",
            "error",
            error_category,
        )

    if decision in {
        "unavailable",
        "consistency_error",
    }:
        return (
            "failed",
            (
                "conflict"
                if decision
                == "consistency_error"
                else "error"
            ),
            error_category,
        )

    return (
        "unknown",
        "unknown",
        "unknown",
    )


def _productive_queue_for_runner_result(
    result: TelegramUpdateRunnerResult,
) -> tuple[str, str, str | None] | None:
    decision = str(
        getattr(
            result,
            "decision",
            "",
        )
        or ""
    ).strip().lower()

    stage = str(
        getattr(
            result,
            "stage",
            "",
        )
        or ""
    ).strip().lower()

    if decision == "idle":
        return None

    idempotent_replay = bool(
        getattr(
            result,
            "idempotent_replay",
            False,
        )
    )

    error_category = (
        _productive_error_category_for_result(
            result
        )
    )

    if stage == "recovery":
        return (
            "recover",
            (
                "error"
                if decision == "unavailable"
                else "success"
            ),
            (
                error_category
                if decision == "unavailable"
                else None
            ),
        )

    if stage == "claim":
        return (
            "claim",
            (
                "success"
                if getattr(
                    result,
                    "update_id",
                    None,
                )
                is not None
                else (
                    "conflict"
                    if decision
                    == "consistency_error"
                    else "error"
                )
            ),
            (
                None
                if getattr(
                    result,
                    "update_id",
                    None,
                )
                is not None
                else error_category
            ),
        )

    if decision == "completed":
        return (
            "acknowledge",
            (
                "duplicate"
                if idempotent_replay
                else "success"
            ),
            None,
        )

    if decision == "retry_scheduled":
        return (
            "release",
            (
                "duplicate"
                if idempotent_replay
                else "success"
            ),
            None,
        )

    if decision == "dead_lettered":
        return (
            "fail",
            (
                "duplicate"
                if idempotent_replay
                else "success"
            ),
            None,
        )

    if decision == "ownership_lost":
        return (
            "release",
            "conflict",
            "optimistic_conflict",
        )

    if decision in {
        "unavailable",
        "consistency_error",
    }:
        return (
            (
                "acknowledge"
                if stage == "complete"
                else "fail"
            ),
            (
                "conflict"
                if decision
                == "consistency_error"
                else "error"
            ),
            error_category,
        )

    return (
        "unknown",
        "unknown",
        "unknown",
    )


def record_productive_receipt_and_queue_result(
    result: TelegramUpdateRunnerResult,
    *,
    operations,
) -> None:
    receipt = (
        _productive_receipt_for_runner_result(
            result
        )
    )

    if receipt is not None:
        (
            receipt_status,
            receipt_outcome,
            receipt_error_category,
        ) = receipt

        operations.record_receipt(
            status=receipt_status,
            outcome=receipt_outcome,
            error_category=(
                receipt_error_category
            ),
        )

    queue_operation = (
        _productive_queue_for_runner_result(
            result
        )
    )

    if queue_operation is not None:
        (
            operation,
            outcome,
            error_category,
        ) = queue_operation

        operations.record_queue_operation(
            operation=operation,
            outcome=outcome,
            error_category=error_category,
        )


def record_productive_runner_result(
    result: TelegramUpdateRunnerResult,
    *,
    operations,
) -> None:
    """
    Converte o contrato seguro do runner em
    métricas agregadas de baixa cardinalidade.
    """
    cycle_result = (
        _productive_cycle_result_for_runner_result(
            result
        )
    )

    operations.record_worker_cycle(
        result=cycle_result,
    )

    update_classification = (
        _productive_update_outcome_for_runner_result(
            result
        )
    )

    if update_classification is None:
        return

    outcome, error_category = (
        update_classification
    )

    operations.record_worker_update(
        outcome=outcome,
        error_category=error_category,
    )


def handle_productive_runner_result(
    result: TelegramUpdateRunnerResult,
    *,
    stream: TextIO,
    operations,
) -> None:
    """
    Callback único do runner.

    Logging e métricas são isolados: falhas da
    telemetria nunca interrompem o processamento.
    """
    try:
        emit_runner_result(
            result,
            stream=stream,
        )
    except Exception:
        pass

    try:
        record_productive_runner_result(
            result,
            operations=operations,
        )
    except Exception:
        pass

    try:
        record_productive_receipt_and_queue_result(
            result,
            operations=operations,
        )
    except Exception:
        pass


def emit_runner_summary(
    summary: TelegramUpdateRunnerSummary,
    *,
    stream: TextIO,
) -> None:
    _emit_event(
        "telegram_worker_summary",
        summary.to_safe_dict(),
        stream=stream,
    )


def _config_to_safe_dict(
    config: TelegramUpdateWorkerConfig,
) -> dict[str, object]:
    return {
        "lease_seconds": (
            config.lease_seconds
        ),
        "idle_sleep_seconds": (
            config.idle_sleep_seconds
        ),
        "unavailable_sleep_seconds": (
            config
            .unavailable_sleep_seconds
        ),
        "recovery_interval_seconds": (
            config
            .recovery_interval_seconds
        ),
        "recovery_batch_size": (
            config.recovery_batch_size
        ),
        "retry_base_delay_seconds": (
            config
            .retry_base_delay_seconds
        ),
        "retry_max_delay_seconds": (
            config
            .retry_max_delay_seconds
        ),
    }


def _install_signal_handlers(
    stop_event: Any,
    *,
    signal_module: Any = signal,
) -> dict[int, Any]:
    if not callable(
        getattr(
            stop_event,
            "set",
            None,
        )
    ):
        raise TelegramUpdateRunnerConfigurationError(
            "O stop_event do worker é inválido."
        )

    previous_handlers: dict[
        int,
        Any,
    ] = {}

    def stop_handler(
        _signal_number,
        _frame,
    ) -> None:
        stop_event.set()

    signal_numbers: list[int] = []

    for attribute_name in (
        "SIGINT",
        "SIGTERM",
    ):
        signal_number = getattr(
            signal_module,
            attribute_name,
            None,
        )

        if (
            isinstance(
                signal_number,
                int,
            )
            and signal_number
            not in signal_numbers
        ):
            signal_numbers.append(
                signal_number
            )

    for signal_number in signal_numbers:
        previous_handlers[
            signal_number
        ] = signal_module.signal(
            signal_number,
            stop_handler,
        )

    return previous_handlers


def _restore_signal_handlers(
    previous_handlers: Mapping[
        int,
        Any,
    ],
    *,
    signal_module: Any = signal,
) -> None:
    for (
        signal_number,
        previous_handler,
    ) in previous_handlers.items():
        try:
            signal_module.signal(
                signal_number,
                previous_handler,
            )

        except Exception:
            continue


def _positive_integer_argument(
    value: str,
) -> int:
    try:
        parsed = int(
            value,
            10,
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        raise argparse.ArgumentTypeError(
            "deve ser um inteiro positivo"
        ) from None

    if parsed < 1:
        raise argparse.ArgumentTypeError(
            "deve ser um inteiro positivo"
        )

    return parsed


def _build_parser() -> (
    argparse.ArgumentParser
):
    parser = argparse.ArgumentParser(
        prog=(
            "run_telegram_update_worker"
        ),
        description=(
            "Executa o worker durável "
            "da fila Telegram da INNA."
        ),
    )

    parser.add_argument(
        "--max-cycles",
        type=_positive_integer_argument,
        default=None,
        help=(
            "Limita os ciclos para smoke tests. "
            "O padrão é execução contínua."
        ),
    )

    return parser



def _load_productive_telegram_processor(
    *,
    stderr: TextIO,
    metrics_runtime: (
        TelegramProductiveMetricsRuntime
        | None
    ) = None,
):
    """
    Compõe o processador produtivo com:

    - structured logging;
    - registry produtivo único por processo;
    - compatibilidade com loaders e mocks antigos.
    """
    resolved_metrics_runtime = (
        metrics_runtime
        or create_production_telegram_metrics_runtime()
    )

    event_sink_factory = lambda: (
        create_production_telegram_event_sink(
            stream=stderr
        )
    )

    metrics_factory = lambda: (
        CompositeTelegramConversationMetrics(
            [
                resolved_metrics_runtime.adapter,
            ]
        )
    )

    loader_kwargs = {}

    try:
        signature = inspect.signature(
            load_telegram_processor
        )
    except (
        TypeError,
        ValueError,
    ):
        signature = None

    if signature is not None:
        try:
            signature.bind(
                event_sink_factory=event_sink_factory
            )
        except TypeError:
            pass
        else:
            loader_kwargs[
                "event_sink_factory"
            ] = event_sink_factory

        try:
            signature.bind(
                metrics_factory=metrics_factory
            )
        except TypeError:
            pass
        else:
            loader_kwargs[
                "metrics_factory"
            ] = metrics_factory

    processor = load_telegram_processor(
        **loader_kwargs
    )

    try:
        setattr(
            processor,
            "_telegram_productive_metrics_runtime",
            resolved_metrics_runtime,
        )
    except Exception:
        pass

    return processor


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    resolved_stdout = (
        stdout
        if stdout is not None
        else sys.stdout
    )

    resolved_stderr = (
        stderr
        if stderr is not None
        else sys.stderr
    )

    parser = _build_parser()

    try:
        arguments = parser.parse_args(
            list(argv)
            if argv is not None
            else None
        )

    except SystemExit as error:
        return int(
            error.code
        )

    try:
        config = (
            load_worker_config_from_env()
        )

        keyring = (
            load_telegram_update_keyring_from_env()
        )

        metrics_runtime = (
            create_production_telegram_metrics_runtime()
        )

        processor = (
            _load_productive_telegram_processor(
                stderr=resolved_stderr,
                metrics_runtime=metrics_runtime,
            )
        )

    except (
        TelegramUpdateJobConfigurationError,
        TelegramUpdateRunnerConfigurationError,
    ):
        _emit_event(
            "telegram_worker_error",
            {
                "error_code": (
                    "telegram.worker_"
                    "configuration_invalid"
                ),
            },
            stream=resolved_stderr,
        )

        return EXIT_CONFIGURATION_ERROR

    except Exception:
        _emit_event(
            "telegram_worker_error",
            {
                "error_code": (
                    "telegram.worker_"
                    "initialization_failed"
                ),
            },
            stream=resolved_stderr,
        )

        return EXIT_RUNTIME_ERROR

    stop_event = Event()
    previous_handlers: dict[
        int,
        Any,
    ] = {}

    try:
        previous_handlers = (
            _install_signal_handlers(
                stop_event
            )
        )

        _emit_event(
            "telegram_worker_started",
            _config_to_safe_dict(
                config
            ),
            stream=resolved_stdout,
        )

        summary = (
            run_telegram_update_worker(
                processor,
                stop_event=stop_event,
                config=config,
                keyring=keyring,
                on_result=lambda result: (
                    handle_productive_runner_result(
                        result,
                        stream=resolved_stdout,
                        operations=(
                            metrics_runtime.operations
                        ),
                    )
                ),
                max_cycles=(
                    arguments.max_cycles
                ),
            )
        )

    except KeyboardInterrupt:
        stop_event.set()

        _emit_event(
            "telegram_worker_stopped",
            {
                "reason": "keyboard_interrupt",
            },
            stream=resolved_stdout,
        )

        return EXIT_INTERRUPTED

    except (
        TelegramUpdateJobConfigurationError,
        TelegramUpdateRunnerConfigurationError,
    ):
        _emit_event(
            "telegram_worker_error",
            {
                "error_code": (
                    "telegram.worker_"
                    "configuration_invalid"
                ),
            },
            stream=resolved_stderr,
        )

        return EXIT_CONFIGURATION_ERROR

    except Exception:
        _emit_event(
            "telegram_worker_error",
            {
                "error_code": (
                    "telegram.worker_"
                    "runtime_failed"
                ),
            },
            stream=resolved_stderr,
        )

        return EXIT_RUNTIME_ERROR

    finally:
        _restore_signal_handlers(
            previous_handlers
        )

    emit_runner_summary(
        summary,
        stream=resolved_stdout,
    )

    return EXIT_OK


__all__ = [
    "ACTIVE_KEY_ENV_NAME",
    "ENV_IDLE_SLEEP_SECONDS",
    "ENV_LEASE_SECONDS",
    "ENV_RECOVERY_BATCH_SIZE",
    "ENV_RECOVERY_INTERVAL_SECONDS",
    "ENV_RETRY_BASE_DELAY_SECONDS",
    "ENV_RETRY_MAX_DELAY_SECONDS",
    "ENV_UNAVAILABLE_SLEEP_SECONDS",
    "EXIT_CONFIGURATION_ERROR",
    "EXIT_INTERRUPTED",
    "EXIT_OK",
    "EXIT_RUNTIME_ERROR",
    "emit_runner_result",
    "emit_runner_summary",
    "load_telegram_processor",
    "load_worker_config_from_env",
    "main",
]
