# F2H5-F7A — Composição produtiva do structured logging

## Resumo

- Parâmetros de `load_telegram_processor`: 3
- Usa `event_sink_factory`: True
- Usa sink NoOp: True
- Usa sink JSON: False
- Definições de logger: 0
- Leituras de ambiente: 0
- Sink JSON exportado: True

## Parâmetros de `load_telegram_processor`

- `metrics_factory`
- `event_sink_factory`
- `clock`

## Imports relevantes

- Linha 7: `import os`
- Linha 9: `import sys`
- Linha 20: `from src.services.telegram_observability import (
    NoOpTelegramConversationMetrics,
    NoOpTelegramOperationalEventSink,
    TelegramConversationMetrics,
    TelegramOperationalEventSink,
)`

## Definições de logger

- Nenhum logger definido.

## Funções-alvo

### `_emit_event`

- Linhas: 403–431
- Assinatura: `event: str, payload: Mapping[str, object], *, stream: TextIO`

```python
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
```

### `emit_runner_result`

- Linhas: 434–452
- Assinatura: `result: TelegramUpdateRunnerResult, *, stream: TextIO`

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

- Linhas: 455–464
- Assinatura: `summary: TelegramUpdateRunnerSummary, *, stream: TextIO`

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

### `load_telegram_processor`

- Linhas: 285–399
- Assinatura: `*, metrics_factory: Callable[[], TelegramConversationMetrics]=NoOpTelegramConversationMetrics, event_sink_factory: Callable[[], TelegramOperationalEventSink]=NoOpTelegramOperationalEventSink, clock: Callable[[], float]=time.perf_counter`

```python
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
```

### `main`

- Linhas: 635–806
- Assinatura: `argv: Sequence[str] | None=None, *, stdout: TextIO | None=None, stderr: TextIO | None=None`

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

## Leituras de ambiente

- Nenhuma leitura de ambiente.
