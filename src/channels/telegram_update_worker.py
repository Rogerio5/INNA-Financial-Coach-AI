from __future__ import annotations

import argparse
import json
import math
import os
import signal
import sys

from collections.abc import (
    Mapping,
    Sequence,
)
from threading import Event
from typing import Any, TextIO

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


def load_telegram_processor():
    """
    Importa o processador somente após a
    configuração do worker ter sido validada.
    """
    from api.telegram_webhook import (
        process_telegram_update,
    )

    if not callable(
        process_telegram_update
    ):
        raise TelegramUpdateRunnerConfigurationError(
            "O processador Telegram é inválido."
        )

    return process_telegram_update


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

        processor = (
            load_telegram_processor()
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
                    emit_runner_result(
                        result,
                        stream=(
                            resolved_stdout
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
