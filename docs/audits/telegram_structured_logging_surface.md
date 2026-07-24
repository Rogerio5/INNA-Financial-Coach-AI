# F2H5-F1 — Superfície atual de structured logging

## Resumo

- Arquivos analisados: 5
- Imports de logging: 0
- Definições de logger: 0
- Chamadas de logging: 0
- Chamadas `print`: 10
- Emissores operacionais: 20
- Escritas em stdout: 0
- Escritas em stderr: 0
- Event sinks encontrados: 4
- Candidatos sensíveis: 1

## Imports de logging

- Nenhum import de logging.

## Chamadas de print

### `api/telegram_webhook.py:760`

- Owner: `send_telegram_message`

```python
print("TELEGRAM_BOT_TOKEN não configurado.")
```

### `api/telegram_webhook.py:752`

- Owner: `safe_record_telegram_event`

```python
print(
            "[telegram-event-log] "
            "Falha segura ao registrar evento."
        )
```

### `api/telegram_webhook.py:1729`

- Owner: `_process_telegram_update_core`

```python
print(
            "[telegram-webhook] "
            "Update inválido descartado."
        )
```

### `api/telegram_webhook.py:2066`

- Owner: `_process_telegram_update_core`

```python
print(
            "[telegram-webhook] "
            "Falha segura ao processar atualização."
        )
```

### `api/telegram_webhook.py:2095`

- Owner: `_fail_claimed_telegram_update_safely`

```python
print(
            "[telegram-webhook] "
            "Falha segura ao atualizar receipt."
        )
```

### `api/telegram_webhook.py:2101`

- Owner: `_fail_claimed_telegram_update_safely`

```python
print(
            "[telegram-webhook] "
            "Falha segura ao atualizar receipt."
        )
```

### `api/telegram_webhook.py:2127`

- Owner: `process_claimed_telegram_update`

```python
print(
            "[telegram-webhook] "
            "Falha segura no worker Telegram."
        )
```

### `api/telegram_webhook.py:2149`

- Owner: `process_claimed_telegram_update`

```python
print(
            "[telegram-webhook] "
            "Falha segura ao concluir receipt."
        )
```

### `api/telegram_webhook.py:2159`

- Owner: `process_claimed_telegram_update`

```python
print(
            "[telegram-webhook] "
            "Falha segura ao concluir receipt."
        )
```

### `src/channels/telegram_update_worker.py:427`

- Owner: `_emit_event`

```python
print(
        serialized,
        file=stream,
        flush=True,
    )
```


## Emissores operacionais

- `api/telegram_webhook.py:760` — `send_telegram_message` — `print`
- `api/telegram_webhook.py:752` — `safe_record_telegram_event` — `print`
- `api/telegram_webhook.py:1729` — `_process_telegram_update_core` — `print`
- `api/telegram_webhook.py:2066` — `_process_telegram_update_core` — `print`
- `api/telegram_webhook.py:2095` — `_fail_claimed_telegram_update_safely` — `print`
- `api/telegram_webhook.py:2101` — `_fail_claimed_telegram_update_safely` — `print`
- `api/telegram_webhook.py:2127` — `process_claimed_telegram_update` — `print`
- `api/telegram_webhook.py:2149` — `process_claimed_telegram_update` — `print`
- `api/telegram_webhook.py:2159` — `process_claimed_telegram_update` — `print`
- `src/channels/telegram_update_worker.py:427` — `_emit_event` — `print`
- `src/channels/telegram_update_worker.py:448` — `emit_runner_result` — `_emit_event`
- `src/channels/telegram_update_worker.py:460` — `emit_runner_summary` — `_emit_event`
- `src/channels/telegram_update_worker.py:801` — `main` — `emit_runner_summary`
- `src/channels/telegram_update_worker.py:724` — `main` — `_emit_event`
- `src/channels/telegram_update_worker.py:684` — `main` — `_emit_event`
- `src/channels/telegram_update_worker.py:698` — `main` — `_emit_event`
- `src/channels/telegram_update_worker.py:755` — `main` — `_emit_event`
- `src/channels/telegram_update_worker.py:769` — `main` — `_emit_event`
- `src/channels/telegram_update_worker.py:783` — `main` — `_emit_event`
- `src/channels/telegram_update_worker.py:739` — `main` — `emit_runner_result`

## Event sinks atuais

### `src/services/telegram_observability/events.py` — `NoOpTelegramOperationalEventSink`

Linhas 10–21

```python
class NoOpTelegramOperationalEventSink:
    """
    Sink padrão sem saída.
    """

    __slots__ = ()

    def emit(
        self,
        event: TelegramOperationalEvent,
    ) -> None:
        del event
```

### `src/services/telegram_observability/events.py` — `InMemoryTelegramOperationalEventSink`

Linhas 24–93

```python
class InMemoryTelegramOperationalEventSink:
    """
    Armazena eventos sanitizados para testes.
    """

    def __init__(self) -> None:
        self._events: list[
            TelegramOperationalEvent
        ] = []

        self._lock = RLock()

    def emit(
        self,
        event: TelegramOperationalEvent,
    ) -> None:
        if not isinstance(
            event,
            TelegramOperationalEvent,
        ):
            raise TypeError(
                "event deve ser TelegramOperationalEvent."
            )

        with self._lock:
            self._events.append(event)

    def snapshot(
        self,
    ) -> tuple[
        TelegramOperationalEvent,
        ...,
    ]:
        with self._lock:
            return tuple(
                self._events
            )

    def clear(self) -> None:
        with self._lock:
            self._events.clear()

    def count(
        self,
        *,
        name: str | None = None,
        component: str | None = None,
        outcome: str | None = None,
        level: str | None = None,
    ) -> int:
        return sum(
            1
            for event in self.snapshot()
            if (
                name is None
                or event.name == name
            )
            and (
                component is None
                or event.component == component
            )
            and (
                outcome is None
                or event.outcome == outcome
            )
            and (
                level is None
                or event.level == level
            )
        )
```

### `src/services/telegram_observability/contracts.py` — `TelegramOperationalEvent`

Linhas 205–273

```python
class TelegramOperationalEvent:
    name: str
    level: str
    component: str
    outcome: str
    fields: Mapping[str, object] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        name = str(
            self.name
        ).strip()

        if not name:
            raise ValueError(
                "name não pode ser vazio."
            )

        if not name.startswith(
            "telegram_"
        ):
            raise ValueError(
                "Eventos Telegram devem começar com telegram_."
            )

        object.__setattr__(
            self,
            "name",
            name,
        )

        object.__setattr__(
            self,
            "level",
            _validate_choice(
                field_name="level",
                value=self.level,
                allowed=ALLOWED_EVENT_LEVELS,
            ),
        )

        object.__setattr__(
            self,
            "component",
            _validate_choice(
                field_name="component",
                value=self.component,
                allowed=ALLOWED_METRIC_COMPONENTS,
            ),
        )

        object.__setattr__(
            self,
            "outcome",
            _validate_choice(
                field_name="outcome",
                value=self.outcome,
                allowed=ALLOWED_OUTCOMES,
            ),
        )

        object.__setattr__(
            self,
            "fields",
            MappingProxyType(
                dict(self.fields)
            ),
        )
```

### `src/services/telegram_observability/contracts.py` — `TelegramOperationalEventSink`

Linhas 288–295

```python
class TelegramOperationalEventSink(
    Protocol
):
    def emit(
        self,
        event: TelegramOperationalEvent,
    ) -> None:
        """Emite um evento operacional sanitizado."""
```


## Candidatos sensíveis

- `api/telegram_webhook.py:760` — `send_telegram_message` — termos=['token']
