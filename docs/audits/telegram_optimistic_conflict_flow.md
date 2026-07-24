# F2H5-E1 — Fluxo de conflito otimista

## Resumo

- Arquivos: 5
- Raises de conflito: 3
- Handlers de conflito: 2
- Chamadas `reload_session`: 2
- Chamadas `save_session`: 3
- Funções candidatas à recuperação: 19

## Raises de conflito

### `src/services/telegram_conversation_state/store.py:65`

- Owner: `__post_init__`

```python
raise TelegramConversationStateValidationError(
                "recovered_from_conflict inválido."
            )
```

### `src/services/telegram_conversation_state/repository.py:537`

- Owner: `create_telegram_conversation_state`

```python
raise TelegramConversationStateConflictError(
                        "Estado conversacional ativo já existe."
                    )
```

### `src/services/telegram_conversation_state/repository.py:641`

- Owner: `save_telegram_conversation_state`

```python
raise TelegramConversationStateConflictError(
                        "Estado ausente, expirado "
                        "ou versão divergente."
                    )
```


## Handlers de conflito

### `api/telegram_webhook.py:1952`

- Owner: `telegram_webhook`
- Exceção: `TelegramUpdateIngressConflictError`

```python
raise HTTPException(
            status_code=409,
            detail=(
                "Conflito no update Telegram."
            ),
        ) from None
```

### `src/services/telegram_conversation_state/store.py:280`

- Owner: `open`
- Exceção: `TelegramConversationStateConflictError`

```python
recovered = self.load(
                normalized_user_id,
                normalized_chat_id,
            ) if recovered is None:
                raise return TelegramConversationStateOpenResult(
                record=recovered,
                created=False,
                recovered_from_conflict=True,
            )
```


## Chamadas de reload

- `api/telegram_webhook.py:1300` — `_sync_and_save_durable_telegram_session` — `conversation_bridge.reload_session(
                durable_session
            )`
- `src/services/telegram_conversation_state/webhook_bridge.py:737` — `reload_session` — `self._get_runtime().reload_session(
                validated_session
            )`

## Chamadas de save

- `api/telegram_webhook.py:1280` — `_sync_and_save_durable_telegram_session`
- `api/telegram_webhook.py:1312` — `_sync_and_save_durable_telegram_session`
- `src/services/telegram_conversation_state/webhook_bridge.py:705` — `save_session`

## Funções candidatas à recuperação

### `api/telegram_webhook.py` — `_sync_and_save_durable_telegram_session`

Linhas 1225–1315

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

### `api/telegram_webhook.py` — `telegram_webhook`

Linhas 1896–1987

```python
async def telegram_webhook(
    request: Request,
    _trusted_webhook: Annotated[
        TrustedTelegramWebhookContext,
        Depends(
            require_trusted_telegram_webhook
        ),
    ],
):
    """
    Autentica e registra o update Telegram
    em uma fila PostgreSQL durável.

    A resposta HTTP somente é enviada depois que
    receipt e job criptografado forem confirmados
    na mesma transação.

    O conteúdo não é processado dentro do request.
    """
    try:
        update = await request.json()

    except Exception:
        raise HTTPException(
            status_code=400,
            detail=(
                "Atualização Telegram inválida."
            ),
        ) from None

    if not isinstance(
        update,
        dict,
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Atualização Telegram inválida."
            ),
        )

    try:
        outcome = (
            enqueue_authenticated_telegram_update_atomic(
                update
            )
        )

    except TelegramUpdateIngressValidationError:
        raise HTTPException(
            status_code=400,
            detail=(
                "Atualização Telegram inválida."
            ),
        ) from None

    except TelegramUpdateIngressConflictError:
        raise HTTPException(
            status_code=409,
            detail=(
                "Conflito no update Telegram."
            ),
        ) from None

    except (
        TelegramUpdateIngressConfigurationError,
        TelegramUpdateIngressConsistencyError,
        TelegramUpdateIngressUnavailableError,
    ):
        raise HTTPException(
            status_code=503,
            detail=(
                "Processamento Telegram "
                "temporariamente indisponível."
            ),
        ) from None

    except Exception:
        raise HTTPException(
            status_code=503,
            detail=(
                "Processamento Telegram "
                "temporariamente indisponível."
            ),
        ) from None

    return {
        "ok": True,
        "accepted": outcome.accepted,
        "duplicate": outcome.duplicate,
        "status": outcome.decision,
    }
```

### `src/services/telegram_conversation_state/webhook_bridge.py` — `_classify_observability_error`

Linhas 172–204

```python
def _classify_observability_error(
    error: BaseException,
) -> str:
    error_name = type(
        error
    ).__name__.lower()

    if "conflict" in error_name:
        return "optimistic_conflict"

    if "timeout" in error_name:
        return "timeout"

    if "unavailable" in error_name:
        return "unavailable"

    if "validation" in error_name:
        return "validation"

    if "identity" in error_name:
        return "identity"

    if "security" in error_name:
        return "security"

    if (
        "repository" in error_name
        or "persistence" in error_name
        or "conversationstate" in error_name
    ):
        return "persistence"

    return "unknown"
```

### `src/services/telegram_conversation_state/webhook_bridge.py` — `_observe_bridge_operation`

Linhas 261–428

```python
def _observe_bridge_operation(
    operation_name: str,
):
    if operation_name not in _BRIDGE_EVENT_NAMES:
        raise ValueError(
            "Operação observável inválida: "
            f"{operation_name!r}."
        )

    event_name = _BRIDGE_EVENT_NAMES[
        operation_name
    ]

    def decorator(
        method: Callable[..., _T],
    ) -> Callable[..., _T]:
        @wraps(method)
        def wrapped(
            self: Any,
            *args: Any,
            **kwargs: Any,
        ) -> _T:
            try:
                started_at = float(
                    self.clock()
                )

            except Exception:
                started_at = 0.0

            try:
                result = method(
                    self,
                    *args,
                    **kwargs,
                )

            except Exception as error:
                duration_ms = (
                    _safe_duration_ms(
                        clock=self.clock,
                        started_at=started_at,
                    )
                )

                error_category = (
                    _classify_observability_error(
                        error
                    )
                )

                is_conflict = (
                    error_category
                    == "optimistic_conflict"
                )

                outcome = (
                    "conflict"
                    if is_conflict
                    else "error"
                )

                record = (
                    TelegramConversationMetricRecord(
                        operation=operation_name,
                        component="bridge",
                        outcome=outcome,
                        duration_ms=duration_ms,
                        error_category=(
                            error_category
                        ),
                        conflict_recovered=(
                            False
                            if is_conflict
                            else None
                        ),
                    )
                )

                _safe_record_bridge_metric(
                    self,
                    record,
                )

                failure_event_name = (
                    "telegram_session_save_conflict"
                    if (
                        operation_name
                        == "save_session"
                        and is_conflict
                    )
                    else event_name
                )

                _safe_emit_bridge_event(
                    self,
                    TelegramOperationalEvent(
                        name=failure_event_name,
                        level=(
                            "warning"
                            if is_conflict
                            else "error"
                        ),
                        component="bridge",
                        outcome=outcome,
                        fields=sanitize_event_fields(
                            {
                                "operation": (
                                    operation_name
                                ),
                                "duration_ms": (
                                    duration_ms
                                ),
                                "error_category": (
                                    error_category
                                ),
                                "conflict_recovered": (
                                    False
                                    if is_conflict
                                    else None
                                ),
                            }
                        ),
                    ),
                )

                raise

            duration_ms = _safe_duration_ms(
                clock=self.clock,
                started_at=started_at,
            )

            _safe_record_bridge_metric(
                self,
                TelegramConversationMetricRecord(
                    operation=operation_name,
                    component="bridge",
                    outcome="success",
                    duration_ms=duration_ms,
                ),
            )

            _safe_emit_bridge_event(
                self,
                TelegramOperationalEvent(
                    name=event_name,
                    level="info",
                    component="bridge",
                    outcome="success",
                    fields=sanitize_event_fields(
                        {
                            "operation": (
                                operation_name
                            ),
                            "duration_ms": (
                                duration_ms
                            ),
                        }
                    ),
                ),
            )

            return result

        return wrapped

    return decorator
```

### `src/services/telegram_conversation_state/webhook_bridge.py` — `reload_session`

Linhas 86–90

```python
def reload_session(
        self,
        session: TelegramConversationSession,
    ) -> TelegramConversationSession | None:
        ...
```

### `src/services/telegram_conversation_state/webhook_bridge.py` — `decorator`

Linhas 274–426

```python
def decorator(
        method: Callable[..., _T],
    ) -> Callable[..., _T]:
        @wraps(method)
        def wrapped(
            self: Any,
            *args: Any,
            **kwargs: Any,
        ) -> _T:
            try:
                started_at = float(
                    self.clock()
                )

            except Exception:
                started_at = 0.0

            try:
                result = method(
                    self,
                    *args,
                    **kwargs,
                )

            except Exception as error:
                duration_ms = (
                    _safe_duration_ms(
                        clock=self.clock,
                        started_at=started_at,
                    )
                )

                error_category = (
                    _classify_observability_error(
                        error
                    )
                )

                is_conflict = (
                    error_category
                    == "optimistic_conflict"
                )

                outcome = (
                    "conflict"
                    if is_conflict
                    else "error"
                )

                record = (
                    TelegramConversationMetricRecord(
                        operation=operation_name,
                        component="bridge",
                        outcome=outcome,
                        duration_ms=duration_ms,
                        error_category=(
                            error_category
                        ),
                        conflict_recovered=(
                            False
                            if is_conflict
                            else None
                        ),
                    )
                )

                _safe_record_bridge_metric(
                    self,
                    record,
                )

                failure_event_name = (
                    "telegram_session_save_conflict"
                    if (
                        operation_name
                        == "save_session"
                        and is_conflict
                    )
                    else event_name
                )

                _safe_emit_bridge_event(
                    self,
                    TelegramOperationalEvent(
                        name=failure_event_name,
                        level=(
                            "warning"
                            if is_conflict
                            else "error"
                        ),
                        component="bridge",
                        outcome=outcome,
                        fields=sanitize_event_fields(
                            {
                                "operation": (
                                    operation_name
                                ),
                                "duration_ms": (
                                    duration_ms
                                ),
                                "error_category": (
                                    error_category
                                ),
                                "conflict_recovered": (
                                    False
                                    if is_conflict
                                    else None
                                ),
                            }
                        ),
                    ),
                )

                raise

            duration_ms = _safe_duration_ms(
                clock=self.clock,
                started_at=started_at,
            )

            _safe_record_bridge_metric(
                self,
                TelegramConversationMetricRecord(
                    operation=operation_name,
                    component="bridge",
                    outcome="success",
                    duration_ms=duration_ms,
                ),
            )

            _safe_emit_bridge_event(
                self,
                TelegramOperationalEvent(
                    name=event_name,
                    level="info",
                    component="bridge",
                    outcome="success",
                    fields=sanitize_event_fields(
                        {
                            "operation": (
                                operation_name
                            ),
                            "duration_ms": (
                                duration_ms
                            ),
                        }
                    ),
                ),
            )

            return result

        return wrapped
```

### `src/services/telegram_conversation_state/webhook_bridge.py` — `reload_session`

Linhas 726–754

```python
def reload_session(
        self,
        session: TelegramConversationSession,
    ) -> TelegramConversationSession | None:
        validated_session = (
            _validate_session(
                session
            )
        )

        result = self._invoke(
            lambda: self._get_runtime().reload_session(
                validated_session
            )
        )

        if result is None:
            return None

        return _validate_session(
            result,
            telegram_user_id=(
                validated_session
                .telegram_user_id
            ),
            chat_id=(
                validated_session.chat_id
            ),
        )
```

### `src/services/telegram_conversation_state/webhook_bridge.py` — `wrapped`

Linhas 278–424

```python
def wrapped(
            self: Any,
            *args: Any,
            **kwargs: Any,
        ) -> _T:
            try:
                started_at = float(
                    self.clock()
                )

            except Exception:
                started_at = 0.0

            try:
                result = method(
                    self,
                    *args,
                    **kwargs,
                )

            except Exception as error:
                duration_ms = (
                    _safe_duration_ms(
                        clock=self.clock,
                        started_at=started_at,
                    )
                )

                error_category = (
                    _classify_observability_error(
                        error
                    )
                )

                is_conflict = (
                    error_category
                    == "optimistic_conflict"
                )

                outcome = (
                    "conflict"
                    if is_conflict
                    else "error"
                )

                record = (
                    TelegramConversationMetricRecord(
                        operation=operation_name,
                        component="bridge",
                        outcome=outcome,
                        duration_ms=duration_ms,
                        error_category=(
                            error_category
                        ),
                        conflict_recovered=(
                            False
                            if is_conflict
                            else None
                        ),
                    )
                )

                _safe_record_bridge_metric(
                    self,
                    record,
                )

                failure_event_name = (
                    "telegram_session_save_conflict"
                    if (
                        operation_name
                        == "save_session"
                        and is_conflict
                    )
                    else event_name
                )

                _safe_emit_bridge_event(
                    self,
                    TelegramOperationalEvent(
                        name=failure_event_name,
                        level=(
                            "warning"
                            if is_conflict
                            else "error"
                        ),
                        component="bridge",
                        outcome=outcome,
                        fields=sanitize_event_fields(
                            {
                                "operation": (
                                    operation_name
                                ),
                                "duration_ms": (
                                    duration_ms
                                ),
                                "error_category": (
                                    error_category
                                ),
                                "conflict_recovered": (
                                    False
                                    if is_conflict
                                    else None
                                ),
                            }
                        ),
                    ),
                )

                raise

            duration_ms = _safe_duration_ms(
                clock=self.clock,
                started_at=started_at,
            )

            _safe_record_bridge_metric(
                self,
                TelegramConversationMetricRecord(
                    operation=operation_name,
                    component="bridge",
                    outcome="success",
                    duration_ms=duration_ms,
                ),
            )

            _safe_emit_bridge_event(
                self,
                TelegramOperationalEvent(
                    name=event_name,
                    level="info",
                    component="bridge",
                    outcome="success",
                    fields=sanitize_event_fields(
                        {
                            "operation": (
                                operation_name
                            ),
                            "duration_ms": (
                                duration_ms
                            ),
                        }
                    ),
                ),
            )

            return result
```

### `src/services/telegram_conversation_state/runtime.py` — `_session_from_record`

Linhas 243–266

```python
def _session_from_record(
    record: TelegramConversationState,
    *,
    created: bool = False,
    recovered_from_conflict: bool = False,
) -> TelegramConversationSession:
    if not isinstance(
        record,
        TelegramConversationState,
    ):
        raise TelegramConversationStateConsistencyError(
            "Registro retornado pelo store inválido."
        )

    return TelegramConversationSession(
        current=record,
        state=record.to_processing_state(),
        language=record.language,
        created=created,
        recovered_from_conflict=(
            recovered_from_conflict
        ),
        deleted=False,
    )
```

### `src/services/telegram_conversation_state/runtime.py` — `__post_init__`

Linhas 49–122

```python
def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.current,
            TelegramConversationState,
        ):
            raise TelegramConversationStateValidationError(
                "current inválido."
            )

        normalized_state = (
            normalize_telegram_state(
                self.state
            )
        )

        normalized_language = (
            normalize_telegram_language(
                self.language
            )
        )

        for field_name, value in (
            (
                "created",
                self.created,
            ),
            (
                "recovered_from_conflict",
                self.recovered_from_conflict,
            ),
            (
                "deleted",
                self.deleted,
            ),
        ):
            if not isinstance(
                value,
                bool,
            ):
                raise TelegramConversationStateValidationError(
                    f"{field_name} inválido."
                )

        if (
            self.created
            and self.recovered_from_conflict
        ):
            raise TelegramConversationStateValidationError(
                "Estado de abertura inconsistente."
            )

        persisted_state = (
            self.current.to_processing_state()
        )

        if normalized_state != persisted_state:
            raise TelegramConversationStateConsistencyError(
                "Estado inicial da sessão "
                "difere do registro persistido."
            )

        if (
            normalized_language
            != self.current.language
        ):
            raise TelegramConversationStateConsistencyError(
                "Idioma inicial da sessão "
                "difere do registro persistido."
            )

        self.state = normalized_state
        self.language = normalized_language
```

### `src/services/telegram_conversation_state/runtime.py` — `to_safe_dict`

Linhas 210–232

```python
def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "telegram_user_id": (
                self.telegram_user_id
            ),
            "chat_id": self.chat_id,
            "language": self.language,
            "state_version": (
                self.state_version
            ),
            "created": self.created,
            "recovered_from_conflict": (
                self.recovered_from_conflict
            ),
            "deleted": self.deleted,
            "dirty": (
                False
                if self.deleted
                else self.is_dirty()
            ),
        }
```

### `src/services/telegram_conversation_state/runtime.py` — `open_session`

Linhas 341–397

```python
def open_session(
        self,
        telegram_user_id: int,
        chat_id: int,
        initial_state: Mapping[str, Any],
        language: str | None = None,
        ttl_seconds: int | None = None,
    ) -> TelegramConversationSession:
        (
            normalized_user_id,
            normalized_chat_id,
        ) = validate_telegram_identity(
            telegram_user_id,
            chat_id,
        )

        normalized_state = (
            normalize_telegram_state(
                initial_state
            )
        )

        normalized_language = (
            normalize_telegram_language(
                language
            )
        )

        resolved_ttl = self._resolve_ttl(
            ttl_seconds
        )

        result = self.store.open(
            telegram_user_id=(
                normalized_user_id
            ),
            chat_id=normalized_chat_id,
            initial_state=normalized_state,
            language=normalized_language,
            ttl_seconds=resolved_ttl,
        )

        if not isinstance(
            result,
            TelegramConversationStateOpenResult,
        ):
            raise TelegramConversationStateConsistencyError(
                "Resultado de abertura do store inválido."
            )

        return _session_from_record(
            result.record,
            created=result.created,
            recovered_from_conflict=(
                result.recovered_from_conflict
            ),
        )
```

### `src/services/telegram_conversation_state/runtime.py` — `save_session`

Linhas 399–476

```python
def save_session(
        self,
        session: TelegramConversationSession,
        *,
        ttl_seconds: int | None = None,
        only_if_changed: bool = True,
    ) -> TelegramConversationSession:
        validated_session = (
            self._require_session(
                session
            )
        )

        if not isinstance(
            only_if_changed,
            bool,
        ):
            raise TelegramConversationStateValidationError(
                "only_if_changed inválido."
            )

        resolved_ttl = self._resolve_ttl(
            ttl_seconds
        )

        if (
            only_if_changed
            and not validated_session.is_dirty()
        ):
            return validated_session

        normalized_state = (
            validated_session
            .to_processing_state()
        )

        normalized_language = (
            normalize_telegram_language(
                validated_session.language
            )
        )

        saved = self.store.save(
            current=validated_session.current,
            state=normalized_state,
            language=normalized_language,
            ttl_seconds=resolved_ttl,
        )

        result = _session_from_record(
            saved,
            created=validated_session.created,
            recovered_from_conflict=(
                validated_session
                .recovered_from_conflict
            ),
        )

        if (
            result.telegram_user_id
            != validated_session.telegram_user_id
            or result.chat_id
            != validated_session.chat_id
        ):
            raise TelegramConversationStateConsistencyError(
                "Identidade alterada durante o save."
            )

        if (
            result.state_version
            != validated_session.state_version + 1
        ):
            raise TelegramConversationStateConsistencyError(
                "Versão alterada incorretamente "
                "durante o save."
            )

        return result
```

### `src/services/telegram_conversation_state/runtime.py` — `reload_session`

Linhas 478–491

```python
def reload_session(
        self,
        session: TelegramConversationSession,
    ) -> TelegramConversationSession | None:
        validated_session = (
            self._require_session(
                session
            )
        )

        return self.load_session(
            validated_session.telegram_user_id,
            validated_session.chat_id,
        )
```

### `src/services/telegram_conversation_state/store.py` — `__post_init__`

Linhas 42–75

```python
def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.record,
            TelegramConversationState,
        ):
            raise TelegramConversationStateValidationError(
                "record inválido."
            )

        if not isinstance(
            self.created,
            bool,
        ):
            raise TelegramConversationStateValidationError(
                "created inválido."
            )

        if not isinstance(
            self.recovered_from_conflict,
            bool,
        ):
            raise TelegramConversationStateValidationError(
                "recovered_from_conflict inválido."
            )

        if (
            self.created
            and self.recovered_from_conflict
        ):
            raise TelegramConversationStateValidationError(
                "Resultado de abertura inconsistente."
            )
```

### `src/services/telegram_conversation_state/store.py` — `to_safe_dict`

Linhas 77–88

```python
def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "record": (
                self.record.to_safe_dict()
            ),
            "created": self.created,
            "recovered_from_conflict": (
                self.recovered_from_conflict
            ),
        }
```

### `src/services/telegram_conversation_state/store.py` — `open`

Linhas 217–311

```python
def open(
        self,
        telegram_user_id: int,
        chat_id: int,
        initial_state: Mapping[str, Any],
        language: str | None = None,
        ttl_seconds: int = (
            DEFAULT_STATE_TTL_SECONDS
        ),
    ) -> TelegramConversationStateOpenResult:
        (
            normalized_user_id,
            normalized_chat_id,
        ) = validate_telegram_identity(
            telegram_user_id,
            chat_id,
        )

        normalized_state = (
            normalize_telegram_state(
                initial_state
            )
        )

        normalized_language = (
            normalize_telegram_language(
                language
            )
        )

        normalized_ttl = (
            validate_state_ttl_seconds(
                ttl_seconds
            )
        )

        existing = self.load(
            normalized_user_id,
            normalized_chat_id,
        )

        if existing is not None:
            return TelegramConversationStateOpenResult(
                record=existing,
                created=False,
                recovered_from_conflict=False,
            )

        try:
            created = (
                create_telegram_conversation_state(
                    telegram_user_id=(
                        normalized_user_id
                    ),
                    chat_id=(
                        normalized_chat_id
                    ),
                    state=normalized_state,
                    language=normalized_language,
                    ttl_seconds=normalized_ttl,
                )
            )

        except TelegramConversationStateConflictError:
            recovered = self.load(
                normalized_user_id,
                normalized_chat_id,
            )

            if recovered is None:
                raise

            return TelegramConversationStateOpenResult(
                record=recovered,
                created=False,
                recovered_from_conflict=True,
            )

        validated_created = (
            _validate_record_identity(
                created,
                telegram_user_id=(
                    normalized_user_id
                ),
                chat_id=(
                    normalized_chat_id
                ),
            )
        )

        return TelegramConversationStateOpenResult(
            record=validated_created,
            created=True,
            recovered_from_conflict=False,
        )
```

### `src/services/telegram_conversation_state/repository.py` — `create_telegram_conversation_state`

Linhas 478–571

```python
def create_telegram_conversation_state(
    telegram_user_id: int,
    chat_id: int,
    state: Mapping[str, Any],
    language: str | None = None,
    ttl_seconds: int = (
        DEFAULT_STATE_TTL_SECONDS
    ),
) -> TelegramConversationState:
    (
        normalized_user_id,
        normalized_chat_id,
    ) = validate_telegram_identity(
        telegram_user_id,
        chat_id,
    )

    serialized_state = _serialize_state(
        state
    )

    normalized_language = (
        normalize_telegram_language(
            language
        )
    )

    normalized_ttl = (
        validate_state_ttl_seconds(
            ttl_seconds
        )
    )

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=False,
        ) as cursor:
            connection = _require_connection(
                cursor
            )

            try:
                cursor.execute(
                    _CREATE_STATE_SQL,
                    (
                        normalized_user_id,
                        normalized_chat_id,
                        serialized_state,
                        normalized_language,
                        normalized_ttl,
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    connection.rollback()

                    raise TelegramConversationStateConflictError(
                        "Estado conversacional ativo já existe."
                    )

                record = _record_from_row(
                    row,
                    expected_telegram_user_id=(
                        normalized_user_id
                    ),
                    expected_chat_id=(
                        normalized_chat_id
                    ),
                )

                connection.commit()

                return record

            except TelegramConversationStateError:
                _safe_rollback(
                    connection
                )
                raise

            except Exception:
                _safe_rollback(
                    connection
                )
                _raise_unavailable()

    except TelegramConversationStateError:
        raise

    except Exception:
        _raise_unavailable()
```

### `src/services/telegram_conversation_state/repository.py` — `save_telegram_conversation_state`

Linhas 574–676

```python
def save_telegram_conversation_state(
    telegram_user_id: int,
    chat_id: int,
    state: Mapping[str, Any],
    language: str | None,
    expected_version: int,
    ttl_seconds: int = (
        DEFAULT_STATE_TTL_SECONDS
    ),
) -> TelegramConversationState:
    (
        normalized_user_id,
        normalized_chat_id,
    ) = validate_telegram_identity(
        telegram_user_id,
        chat_id,
    )

    serialized_state = _serialize_state(
        state
    )

    normalized_language = (
        normalize_telegram_language(
            language
        )
    )

    normalized_version = (
        validate_expected_version(
            expected_version
        )
    )

    normalized_ttl = (
        validate_state_ttl_seconds(
            ttl_seconds
        )
    )

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=False,
        ) as cursor:
            connection = _require_connection(
                cursor
            )

            try:
                cursor.execute(
                    _SAVE_STATE_SQL,
                    (
                        serialized_state,
                        normalized_language,
                        normalized_ttl,
                        normalized_user_id,
                        normalized_chat_id,
                        normalized_version,
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    connection.rollback()

                    raise TelegramConversationStateConflictError(
                        "Estado ausente, expirado "
                        "ou versão divergente."
                    )

                record = _record_from_row(
                    row,
                    expected_telegram_user_id=(
                        normalized_user_id
                    ),
                    expected_chat_id=(
                        normalized_chat_id
                    ),
                )

                connection.commit()

                return record

            except TelegramConversationStateError:
                _safe_rollback(
                    connection
                )
                raise

            except Exception:
                _safe_rollback(
                    connection
                )
                _raise_unavailable()

    except TelegramConversationStateError:
        raise

    except Exception:
        _raise_unavailable()
```

