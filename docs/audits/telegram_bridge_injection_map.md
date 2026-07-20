# F2H5-D2 — Mapa de injeção da bridge

Arquivo: `src/services/telegram_conversation_state/webhook_bridge.py`

Classe: `TelegramWebhookConversationBridge`

## Decoradores

- `dataclass(
    slots=True,
)`

## Campos atuais

| Campo | Tipo | Default | Linha |
|---|---|---|---:|
| `runtime_factory` | `Callable[[], TelegramConversationStateRuntimePort]` | `field(repr=False)` | 144 |
| `default_language` | `str` | `'pt-BR'` | 151 |
| `_runtime` | `TelegramConversationStateRuntimePort | None` | `field(default=None, init=False, repr=False)` | 153 |
| `_runtime_lock` | `Any` | `field(default_factory=threading.Lock, init=False, repr=False)` | 162 |

## Referências existentes de observabilidade

- Nenhuma referência existente.

## Métodos

### `__post_init__`

- Linhas: 168–191
- Assinatura: `def __post_init__(self) -> None`
- Chamadas internas: 4
- Raises: 2
- Excepts: 0
- Returns: 0

```python
def __post_init__(
        self,
    ) -> None:
        if not callable(
            self.runtime_factory
        ):
            raise TelegramConversationStateValidationError(
                "runtime_factory inválido."
            )

        normalized_language = (
            normalize_telegram_language(
                self.default_language
            )
        )

        if normalized_language is None:
            raise TelegramConversationStateValidationError(
                "default_language é obrigatório."
            )

        self.default_language = (
            normalized_language
        )
```

### `load_session`

- Linhas: 199–230
- Assinatura: `def load_session(self, telegram_user_id: int, chat_id: int) -> TelegramConversationSession | None`
- Chamadas internas: 5
- Raises: 0
- Excepts: 0
- Returns: 2

```python
def load_session(
        self,
        telegram_user_id: int,
        chat_id: int,
    ) -> TelegramConversationSession | None:
        (
            normalized_user_id,
            normalized_chat_id,
        ) = validate_telegram_identity(
            telegram_user_id,
            chat_id,
        )

        result = self._invoke(
            lambda: self._get_runtime().load_session(
                normalized_user_id,
                normalized_chat_id,
            )
        )

        if result is None:
            return None

        return _validate_session(
            result,
            telegram_user_id=(
                normalized_user_id
            ),
            chat_id=(
                normalized_chat_id
            ),
        )
```

### `open_session`

- Linhas: 232–296
- Assinatura: `def open_session(self, telegram_user_id: int, chat_id: int, initial_state: Mapping[str, Any], language: str | None=None, ttl_seconds: int | None=None) -> TelegramConversationSession`
- Chamadas internas: 8
- Raises: 0
- Excepts: 0
- Returns: 1

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

        normalized_ttl = (
            None
            if ttl_seconds is None
            else validate_state_ttl_seconds(
                ttl_seconds
            )
        )

        result = self._invoke(
            lambda: self._get_runtime().open_session(
                telegram_user_id=(
                    normalized_user_id
                ),
                chat_id=(
                    normalized_chat_id
                ),
                initial_state=(
                    normalized_state
                ),
                language=(
                    normalized_language
                ),
                ttl_seconds=(
                    normalized_ttl
                ),
            )
        )

        return _validate_session(
            result,
            telegram_user_id=(
                normalized_user_id
            ),
            chat_id=(
                normalized_chat_id
            ),
        )
```

### `load_or_open_session`

- Linhas: 298–350
- Assinatura: `def load_or_open_session(self, telegram_user_id: int, chat_id: int, initial_state: Mapping[str, Any], language: str | None=None, ttl_seconds: int | None=None) -> TelegramConversationSession`
- Chamadas internas: 6
- Raises: 0
- Excepts: 0
- Returns: 2

```python
def load_or_open_session(
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

        normalized_ttl = (
            None
            if ttl_seconds is None
            else validate_state_ttl_seconds(
                ttl_seconds
            )
        )

        existing = self.load_session(
            normalized_user_id,
            normalized_chat_id,
        )

        if existing is not None:
            return existing

        return self.open_session(
            telegram_user_id=(
                normalized_user_id
            ),
            chat_id=normalized_chat_id,
            initial_state=normalized_state,
            language=normalized_language,
            ttl_seconds=normalized_ttl,
        )
```

### `save_session`

- Linhas: 352–411
- Assinatura: `def save_session(self, session: TelegramConversationSession, *, ttl_seconds: int | None=None, only_if_changed: bool=True) -> TelegramConversationSession`
- Chamadas internas: 10
- Raises: 2
- Excepts: 0
- Returns: 1

```python
def save_session(
        self,
        session: TelegramConversationSession,
        *,
        ttl_seconds: int | None = None,
        only_if_changed: bool = True,
    ) -> TelegramConversationSession:
        # Entrada pública inválida é erro de validação.
        # ConsistencyError fica reservado para dados
        # inconsistentes retornados pelo runtime/store.
        if not isinstance(
            session,
            TelegramConversationSession,
        ):
            raise TelegramConversationStateValidationError(
                "Sessão informada para persistência é inválida."
            )

        validated_session = (
            _validate_session(
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

        normalized_ttl = (
            None
            if ttl_seconds is None
            else validate_state_ttl_seconds(
                ttl_seconds
            )
        )

        result = self._invoke(
            lambda: self._get_runtime().save_session(
                validated_session,
                ttl_seconds=normalized_ttl,
                only_if_changed=(
                    only_if_changed
                ),
            )
        )

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

### `reload_session`

- Linhas: 413–441
- Assinatura: `def reload_session(self, session: TelegramConversationSession) -> TelegramConversationSession | None`
- Chamadas internas: 5
- Raises: 0
- Excepts: 0
- Returns: 2

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

### `delete_session`

- Linhas: 443–472
- Assinatura: `def delete_session(self, session: TelegramConversationSession) -> bool`
- Chamadas internas: 7
- Raises: 2
- Excepts: 0
- Returns: 1

```python
def delete_session(
        self,
        session: TelegramConversationSession,
    ) -> bool:
        validated_session = (
            _validate_session(
                session
            )
        )

        deleted = self._invoke(
            lambda: self._get_runtime().delete_session(
                validated_session
            )
        )

        if not isinstance(
            deleted,
            bool,
        ):
            raise TelegramConversationStateConsistencyError(
                "Resultado de exclusão do runtime inválido."
            )

        if not validated_session.deleted:
            raise TelegramConversationStateConsistencyError(
                "Runtime não invalidou a sessão removida."
            )

        return deleted
```

### `delete_identity`

- Linhas: 474–502
- Assinatura: `def delete_identity(self, telegram_user_id: int, chat_id: int) -> bool`
- Chamadas internas: 6
- Raises: 1
- Excepts: 0
- Returns: 1

```python
def delete_identity(
        self,
        telegram_user_id: int,
        chat_id: int,
    ) -> bool:
        (
            normalized_user_id,
            normalized_chat_id,
        ) = validate_telegram_identity(
            telegram_user_id,
            chat_id,
        )

        deleted = self._invoke(
            lambda: self._get_runtime().delete_identity(
                normalized_user_id,
                normalized_chat_id,
            )
        )

        if not isinstance(
            deleted,
            bool,
        ):
            raise TelegramConversationStateConsistencyError(
                "Resultado de exclusão do runtime inválido."
            )

        return deleted
```

### `resolve_language`

- Linhas: 504–543
- Assinatura: `def resolve_language(self, telegram_user_id: int, chat_id: int, *, fallback_language: str | None=None) -> str`
- Chamadas internas: 4
- Raises: 1
- Excepts: 0
- Returns: 2

```python
def resolve_language(
        self,
        telegram_user_id: int,
        chat_id: int,
        *,
        fallback_language: str | None = None,
    ) -> str:
        (
            normalized_user_id,
            normalized_chat_id,
        ) = validate_telegram_identity(
            telegram_user_id,
            chat_id,
        )

        resolved_fallback = (
            self.default_language
            if fallback_language is None
            else normalize_telegram_language(
                fallback_language
            )
        )

        if resolved_fallback is None:
            raise TelegramConversationStateValidationError(
                "fallback_language é obrigatório."
            )

        session = self.load_session(
            normalized_user_id,
            normalized_chat_id,
        )

        if (
            session is None
            or session.language is None
        ):
            return resolved_fallback

        return session.language
```

### `cleanup_expired`

- Linhas: 545–578
- Assinatura: `def cleanup_expired(self, limit: int=100) -> int`
- Chamadas internas: 7
- Raises: 1
- Excepts: 0
- Returns: 1

```python
def cleanup_expired(
        self,
        limit: int = 100,
    ) -> int:
        normalized_limit = (
            validate_cleanup_limit(
                limit
            )
        )

        deleted_count = self._invoke(
            lambda: self._get_runtime().cleanup_expired(
                normalized_limit
            )
        )

        if (
            isinstance(
                deleted_count,
                bool,
            )
            or not isinstance(
                deleted_count,
                int,
            )
            or deleted_count < 0
            or deleted_count
            > normalized_limit
        ):
            raise TelegramConversationStateConsistencyError(
                "Resultado de cleanup do runtime inválido."
            )

        return deleted_count
```

### `to_safe_dict`

- Linhas: 580–590
- Assinatura: `def to_safe_dict(self) -> dict[str, object]`
- Chamadas internas: 0
- Raises: 0
- Excepts: 0
- Returns: 1

```python
def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "default_language": (
                self.default_language
            ),
            "runtime_initialized": (
                self.runtime_initialized
            ),
        }
```

### `_get_runtime`

- Linhas: 592–628
- Assinatura: `def _get_runtime(self) -> TelegramConversationStateRuntimePort`
- Chamadas internas: 4
- Raises: 3
- Excepts: 2
- Returns: 3

```python
def _get_runtime(
        self,
    ) -> TelegramConversationStateRuntimePort:
        existing = self._runtime

        if existing is not None:
            return existing

        with self._runtime_lock:
            existing = self._runtime

            if existing is not None:
                return existing

            try:
                created = self.runtime_factory()

            except TelegramConversationStateError:
                raise

            except Exception:
                raise TelegramConversationStateUnavailableError(
                    "Runtime conversacional "
                    "temporariamente indisponível."
                ) from None

            if not isinstance(
                created,
                TelegramConversationStateRuntimePort,
            ):
                raise TelegramConversationStateConsistencyError(
                    "Factory retornou runtime inválido."
                )

            self._runtime = created

            return created
```

### `_invoke`

- Linhas: 631–647
- Assinatura: `@staticmethod`
- Chamadas internas: 2
- Raises: 2
- Excepts: 2
- Returns: 1

```python
def _invoke(
        operation: Callable[
            [],
            _T,
        ],
    ) -> _T:
        try:
            return operation()

        except TelegramConversationStateError:
            raise

        except Exception:
            raise TelegramConversationStateUnavailableError(
                "Persistência conversacional "
                "temporariamente indisponível."
            ) from None
```

