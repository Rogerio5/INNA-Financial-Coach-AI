# F2H5-D5A — Composição observável no worker

Arquivo: `src/channels/telegram_update_worker.py`

## Resumo

- Imports: 11
- Funções: 14
- Classes: 0
- Referências à bridge: 2
- Construções da bridge: 1
- Referências de observabilidade: 0
- Factories PostgreSQL: 1

## Imports

- Linha 1: `from __future__ import annotations`
- Linha 3: `import argparse`
- Linha 4: `import json`
- Linha 5: `import math`
- Linha 6: `import os`
- Linha 7: `import signal`
- Linha 8: `import sys`
- Linha 10: `from collections.abc import (
    Mapping,
    Sequence,
)`
- Linha 14: `from threading import Event`
- Linha 15: `from typing import Any, TextIO`
- Linha 17: `from src.services.telegram_update_jobs import (
    TelegramUpdateJobConfigurationError,
    TelegramUpdateRunnerConfigurationError,
    TelegramUpdateRunnerResult,
    TelegramUpdateRunnerSummary,
    TelegramUpdateWorkerConfig,
    load_telegram_update_keyring_from_env,
    run_telegram_update_worker,
)`

## Construções da bridge

### Linha 262

- Chamada: `create_postgres_telegram_webhook_conversation_bridge`
- Keywords: ``

```python
create_postgres_telegram_webhook_conversation_bridge()
```


## Referências de observabilidade atuais

- Nenhuma referência atual.

## Factories PostgreSQL

- Linha 262: `create_postgres_telegram_webhook_conversation_bridge`

## Funções candidatas à injeção

### `load_worker_config_from_env`

- Linhas: 147–225
- Assinatura: `def load_worker_config_from_env(environment: Mapping[str, str] | None=None) -> TelegramUpdateWorkerConfig`

```python
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
```

### `load_telegram_processor`

- Linhas: 228–283
- Assinatura: `def load_telegram_processor()`

```python
def load_telegram_processor():
    """
    Compõe o processador produtivo do worker.

    A bridge é criada uma única vez durante a inicialização do processo
    e reutilizada em todos os jobs processados por esta instância.

    A factory da bridge mantém a inicialização do runtime PostgreSQL
    lazy: importar este módulo ou construir o wrapper não deve abrir uma
    conexão com o banco antecipadamente.
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

    try:
        conversation_bridge = (
            create_postgres_telegram_webhook_conversation_bridge()
        )

    except Exception:
        raise TelegramUpdateRunnerConfigurationError(
            "Não foi possível compor o estado conversacional durável."
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
```

### `emit_runner_result`

- Linhas: 318–336
- Assinatura: `def emit_runner_result(result: TelegramUpdateRunnerResult, *, stream: TextIO) -> None`

```python
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
```

### `emit_runner_summary`

- Linhas: 339–348
- Assinatura: `def emit_runner_summary(summary: TelegramUpdateRunnerSummary, *, stream: TextIO) -> None`

```python
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
```

### `_build_parser`

- Linhas: 493–516
- Assinatura: `def _build_parser() -> argparse.ArgumentParser`

```python
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
```

### `main`

- Linhas: 519–690
- Assinatura: `def main(argv: Sequence[str] | None=None, *, stdout: TextIO | None=None, stderr: TextIO | None=None) -> int`

```python
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
```

