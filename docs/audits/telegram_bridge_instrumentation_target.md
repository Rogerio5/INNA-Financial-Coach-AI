# F2H5-D1 — Alvos de instrumentação da bridge

Arquivo: `src/services/telegram_conversation_state/webhook_bridge.py`

## Imports atuais

- `from __future__ import annotations`
- `import threading`
- `from collections.abc import (
    Callable,
    Mapping,
)`
- `from dataclasses import (
    dataclass,
    field,
)`
- `from typing import (
    Any,
    Protocol,
    TypeVar,
    runtime_checkable,
)`
- `from .contracts import (
    DEFAULT_STATE_TTL_SECONDS,
    TelegramConversationStateConsistencyError,
    TelegramConversationStateError,
    TelegramConversationStateUnavailableError,
    TelegramConversationStateValidationError,
    normalize_telegram_language,
    normalize_telegram_state,
    validate_cleanup_limit,
    validate_state_ttl_seconds,
    validate_telegram_identity,
)`
- `from .runtime import (
    TelegramConversationSession,
    create_postgres_telegram_conversation_state_runtime,
)`

## Classes

### `TelegramConversationStateRuntimePort` — linha 45

- `def load_session(self, telegram_user_id: int, chat_id: int) -> TelegramConversationSession | None`
- `def open_session(self, telegram_user_id: int, chat_id: int, initial_state: Mapping[str, Any], language: str | None = None, ttl_seconds: int | None = None) -> TelegramConversationSession`
- `def save_session(self, session: TelegramConversationSession, *, ttl_seconds: int | None = None, only_if_changed: bool = True) -> TelegramConversationSession`
- `def reload_session(self, session: TelegramConversationSession) -> TelegramConversationSession | None`
- `def delete_session(self, session: TelegramConversationSession) -> bool`
- `def delete_identity(self, telegram_user_id: int, chat_id: int) -> bool`
- `def cleanup_expired(self, limit: int = 100) -> int`

### `TelegramWebhookConversationBridge` — linha 143

- `def __post_init__(self) -> None`
- `def runtime_initialized(self) -> bool`
- `def load_session(self, telegram_user_id: int, chat_id: int) -> TelegramConversationSession | None`
- `def open_session(self, telegram_user_id: int, chat_id: int, initial_state: Mapping[str, Any], language: str | None = None, ttl_seconds: int | None = None) -> TelegramConversationSession`
- `def load_or_open_session(self, telegram_user_id: int, chat_id: int, initial_state: Mapping[str, Any], language: str | None = None, ttl_seconds: int | None = None) -> TelegramConversationSession`
- `def save_session(self, session: TelegramConversationSession, *, ttl_seconds: int | None = None, only_if_changed: bool = True) -> TelegramConversationSession`
- `def reload_session(self, session: TelegramConversationSession) -> TelegramConversationSession | None`
- `def delete_session(self, session: TelegramConversationSession) -> bool`
- `def delete_identity(self, telegram_user_id: int, chat_id: int) -> bool`
- `def resolve_language(self, telegram_user_id: int, chat_id: int, *, fallback_language: str | None = None) -> str`
- `def cleanup_expired(self, limit: int = 100) -> int`
- `def to_safe_dict(self) -> dict[str, object]`
- `def _get_runtime(self) -> TelegramConversationStateRuntimePort`
- `def _invoke(operation: Callable[[], _T]) -> _T`

## Métodos obrigatórios

### `_get_runtime` — ocorrência 1

- Linha inicial: 592
- Linha final: 628
- Assinatura: `def _get_runtime(self) -> TelegramConversationStateRuntimePort`

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

### `_invoke` — ocorrência 1

- Linha inicial: 631
- Linha final: 647
- Assinatura: `def _invoke(operation: Callable[[], _T]) -> _T`

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

### `delete_session` — ocorrência 1

- Linha inicial: 80
- Linha final: 84
- Assinatura: `def delete_session(self, session: TelegramConversationSession) -> bool`

```python
def delete_session(
        self,
        session: TelegramConversationSession,
    ) -> bool:
        ...
```

### `delete_session` — ocorrência 2

- Linha inicial: 443
- Linha final: 472
- Assinatura: `def delete_session(self, session: TelegramConversationSession) -> bool`

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

### `load_or_open_session` — ocorrência 1

- Linha inicial: 298
- Linha final: 350
- Assinatura: `def load_or_open_session(self, telegram_user_id: int, chat_id: int, initial_state: Mapping[str, Any], language: str | None = None, ttl_seconds: int | None = None) -> TelegramConversationSession`

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

### `reload_session` — ocorrência 1

- Linha inicial: 74
- Linha final: 78
- Assinatura: `def reload_session(self, session: TelegramConversationSession) -> TelegramConversationSession | None`

```python
def reload_session(
        self,
        session: TelegramConversationSession,
    ) -> TelegramConversationSession | None:
        ...
```

### `reload_session` — ocorrência 2

- Linha inicial: 413
- Linha final: 441
- Assinatura: `def reload_session(self, session: TelegramConversationSession) -> TelegramConversationSession | None`

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

### `resolve_language` — ocorrência 1

- Linha inicial: 504
- Linha final: 543
- Assinatura: `def resolve_language(self, telegram_user_id: int, chat_id: int, *, fallback_language: str | None = None) -> str`

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

### `save_session` — ocorrência 1

- Linha inicial: 65
- Linha final: 72
- Assinatura: `def save_session(self, session: TelegramConversationSession, *, ttl_seconds: int | None = None, only_if_changed: bool = True) -> TelegramConversationSession`

```python
def save_session(
        self,
        session: TelegramConversationSession,
        *,
        ttl_seconds: int | None = None,
        only_if_changed: bool = True,
    ) -> TelegramConversationSession:
        ...
```

### `save_session` — ocorrência 2

- Linha inicial: 352
- Linha final: 411
- Assinatura: `def save_session(self, session: TelegramConversationSession, *, ttl_seconds: int | None = None, only_if_changed: bool = True) -> TelegramConversationSession`

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

