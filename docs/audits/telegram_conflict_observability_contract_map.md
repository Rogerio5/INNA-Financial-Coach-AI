# F2H5-E2 — Contratos formais de conflito

## Resumo

- Contratos: 2
- Protocolos: 2
- Implementações: 4
- Imports observáveis no webhook: 0
- Referências de observabilidade na recuperação: 0

## Contratos

### `src/services/telegram_observability/contracts.py` — `TelegramConversationMetricRecord`

```python
class TelegramConversationMetricRecord:
    operation: str
    component: str
    outcome: str
    duration_ms: float
    error_category: str | None = None
    conflict_recovered: bool | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "operation",
            _validate_choice(
                field_name="operation",
                value=self.operation,
                allowed=ALLOWED_METRIC_OPERATIONS,
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
            "duration_ms",
            _validate_duration(
                self.duration_ms
            ),
        )

        if self.error_category is not None:
            object.__setattr__(
                self,
                "error_category",
                _validate_choice(
                    field_name="error_category",
                    value=self.error_category,
                    allowed=ALLOWED_ERROR_CATEGORIES,
                ),
            )

        if (
            self.outcome
            in {
                "error",
                "conflict",
            }
            and self.error_category is None
        ):
            raise ValueError(
                "error_category é obrigatória "
                "para outcomes error ou conflict."
            )

        if (
            self.conflict_recovered is not None
            and self.outcome
            not in {
                "conflict",
                "recovered",
            }
        ):
            raise ValueError(
                "conflict_recovered somente pode ser "
                "usado em conflito ou recuperação."
            )
```

### `src/services/telegram_observability/contracts.py` — `TelegramOperationalEvent`

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

## Protocolos

### `src/services/telegram_observability/contracts.py` — `TelegramConversationMetrics`

```python
class TelegramConversationMetrics(
    Protocol
):
    def record_operation(
        self,
        record: TelegramConversationMetricRecord,
    ) -> None:
        """Registra uma operação observável."""
```

### `src/services/telegram_observability/contracts.py` — `TelegramOperationalEventSink`

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

## Imports atuais no webhook

- Nenhum import direto de observabilidade.

## Função de recuperação

- Linhas: 1225–1315
- Assinatura: `def _sync_and_save_durable_telegram_session(*, conversation_bridge: 'TelegramWebhookConversationBridge', durable_session, processing_state: dict, language: str | None=None)`

```python
def _sync_and_save_durable_telegram_session(
    *,
    conversation_bridge: "TelegramWebhookConversationBridge",
    durable_session,
    processing_state: dict,
    language: str | None = None,
):
    """
    Persiste uma transição com uma única recuperação de conflito.

    Em conflito otimista, recarrega a sessão mais recente, reaplica a
    transição atual e tenta salvar uma segunda e última vez.
    """
    if conversation_bridge is None:
        raise ValueError(
            "conversation_bridge é obrigatória."
        )

    if durable_session is None:
        raise ValueError(
            "durable_session é obrigatória."
        )

    if not isinstance(
        processing_state,
        dict,
    ):
        raise TypeError(
            "processing_state deve ser um dict."
        )

    resolved_language = (
        language
        if language is not None
        else processing_state.get("lang")
    )

    def apply_transition(
        target_session,
    ):
        target_session.replace_state(
            processing_state
        )

        target_session.set_language(
            resolved_language
        )

        return target_session

    apply_transition(
        durable_session
    )

    try:
        return conversation_bridge.save_session(
            durable_session,
            only_if_changed=True,
        )

    except Exception as error:
        conflict_type = (
            TelegramConversationStateConflictError
        )

        if (
            conflict_type is None
            or not isinstance(
                error,
                conflict_type,
            )
        ):
            raise

        reloaded_session = (
            conversation_bridge.reload_session(
                durable_session
            )
        )

        if reloaded_session is None:
            raise

        apply_transition(
            reloaded_session
        )

        return conversation_bridge.save_session(
            reloaded_session,
            only_if_changed=True,
        )
```

## Chamadas internas

- Linha 1275: `apply_transition`
- Linha 1239: `ValueError`
- Linha 1244: `ValueError`
- Linha 1248: `isinstance`
- Linha 1252: `TypeError`
- Linha 1259: `get`
- Linha 1265: `replace_state`
- Linha 1269: `set_language`
- Linha 1280: `save_session`
- Linha 1300: `reload_session`
- Linha 1308: `apply_transition`
- Linha 1312: `save_session`
- Linha 1292: `isinstance`

## Handlers

### Linha 1285 — `Exception`

```python
except Exception as error:
        conflict_type = (
            TelegramConversationStateConflictError
        )

        if (
            conflict_type is None
            or not isinstance(
                error,
                conflict_type,
            )
        ):
            raise

        reloaded_session = (
            conversation_bridge.reload_session(
                durable_session
            )
        )

        if reloaded_session is None:
            raise

        apply_transition(
            reloaded_session
        )

        return conversation_bridge.save_session(
            reloaded_session,
            only_if_changed=True,
        )
```

