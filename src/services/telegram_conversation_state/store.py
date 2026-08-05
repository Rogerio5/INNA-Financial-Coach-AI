from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import (
    Any,
    Protocol,
    runtime_checkable,
)

from .contracts import (
    DEFAULT_STATE_TTL_SECONDS,
    TelegramConversationState,
    TelegramConversationStateConflictError,
    TelegramConversationStateConsistencyError,
    TelegramConversationStateValidationError,
    normalize_telegram_language,
    normalize_telegram_state,
    validate_cleanup_limit,
    validate_state_ttl_seconds,
    validate_telegram_identity,
)

from .repository import (
    create_telegram_conversation_state,
    delete_expired_telegram_conversation_states,
    delete_telegram_conversation_state,
    load_telegram_conversation_state,
    save_telegram_conversation_state,
)


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramConversationStateOpenResult:
    record: TelegramConversationState
    created: bool
    recovered_from_conflict: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.record,
            TelegramConversationState,
        ):
            raise TelegramConversationStateValidationError("record inválido.")

        if not isinstance(
            self.created,
            bool,
        ):
            raise TelegramConversationStateValidationError("created inválido.")

        if not isinstance(
            self.recovered_from_conflict,
            bool,
        ):
            raise TelegramConversationStateValidationError(
                "recovered_from_conflict inválido."
            )

        if self.created and self.recovered_from_conflict:
            raise TelegramConversationStateValidationError(
                "Resultado de abertura inconsistente."
            )

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "record": (self.record.to_safe_dict()),
            "created": self.created,
            "recovered_from_conflict": (self.recovered_from_conflict),
        }


@runtime_checkable
class TelegramConversationStateStore(Protocol):
    def load(
        self,
        telegram_user_id: int,
        chat_id: int,
    ) -> TelegramConversationState | None: ...

    def open(
        self,
        telegram_user_id: int,
        chat_id: int,
        initial_state: Mapping[str, Any],
        language: str | None = None,
        ttl_seconds: int = (DEFAULT_STATE_TTL_SECONDS),
    ) -> TelegramConversationStateOpenResult: ...

    def save(
        self,
        current: TelegramConversationState,
        state: Mapping[str, Any],
        language: str | None,
        ttl_seconds: int = (DEFAULT_STATE_TTL_SECONDS),
    ) -> TelegramConversationState: ...

    def delete(
        self,
        telegram_user_id: int,
        chat_id: int,
    ) -> bool: ...

    def cleanup_expired(
        self,
        limit: int = 100,
    ) -> int: ...


def _require_record(
    value: Any,
    *,
    field_name: str,
) -> TelegramConversationState:
    if not isinstance(
        value,
        TelegramConversationState,
    ):
        raise TelegramConversationStateValidationError(f"{field_name} inválido.")

    return value


def _validate_record_identity(
    record: TelegramConversationState,
    *,
    telegram_user_id: int,
    chat_id: int,
) -> TelegramConversationState:
    validated = _require_record(
        record,
        field_name="record",
    )

    if validated.telegram_user_id != telegram_user_id or validated.chat_id != chat_id:
        raise TelegramConversationStateConsistencyError(
            "Identidade conversacional inconsistente."
        )

    return validated


@dataclass(
    frozen=True,
    slots=True,
)
class PostgresTelegramConversationStateStore:
    def load(
        self,
        telegram_user_id: int,
        chat_id: int,
    ) -> TelegramConversationState | None:
        (
            normalized_user_id,
            normalized_chat_id,
        ) = validate_telegram_identity(
            telegram_user_id,
            chat_id,
        )

        record = load_telegram_conversation_state(
            normalized_user_id,
            normalized_chat_id,
        )

        if record is None:
            return None

        return _validate_record_identity(
            record,
            telegram_user_id=(normalized_user_id),
            chat_id=(normalized_chat_id),
        )

    def open(
        self,
        telegram_user_id: int,
        chat_id: int,
        initial_state: Mapping[str, Any],
        language: str | None = None,
        ttl_seconds: int = (DEFAULT_STATE_TTL_SECONDS),
    ) -> TelegramConversationStateOpenResult:
        (
            normalized_user_id,
            normalized_chat_id,
        ) = validate_telegram_identity(
            telegram_user_id,
            chat_id,
        )

        normalized_state = normalize_telegram_state(initial_state)

        normalized_language = normalize_telegram_language(language)

        normalized_ttl = validate_state_ttl_seconds(ttl_seconds)

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
            created = create_telegram_conversation_state(
                telegram_user_id=(normalized_user_id),
                chat_id=(normalized_chat_id),
                state=normalized_state,
                language=normalized_language,
                ttl_seconds=normalized_ttl,
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

        validated_created = _validate_record_identity(
            created,
            telegram_user_id=(normalized_user_id),
            chat_id=(normalized_chat_id),
        )

        return TelegramConversationStateOpenResult(
            record=validated_created,
            created=True,
            recovered_from_conflict=False,
        )

    def save(
        self,
        current: TelegramConversationState,
        state: Mapping[str, Any],
        language: str | None,
        ttl_seconds: int = (DEFAULT_STATE_TTL_SECONDS),
    ) -> TelegramConversationState:
        validated_current = _require_record(
            current,
            field_name="current",
        )

        normalized_state = normalize_telegram_state(state)

        normalized_language = normalize_telegram_language(language)

        normalized_ttl = validate_state_ttl_seconds(ttl_seconds)

        saved = save_telegram_conversation_state(
            telegram_user_id=(validated_current.telegram_user_id),
            chat_id=(validated_current.chat_id),
            state=normalized_state,
            language=normalized_language,
            expected_version=(validated_current.state_version),
            ttl_seconds=normalized_ttl,
        )

        validated_saved = _validate_record_identity(
            saved,
            telegram_user_id=(validated_current.telegram_user_id),
            chat_id=(validated_current.chat_id),
        )

        expected_next_version = validated_current.state_version + 1

        if validated_saved.state_version != expected_next_version:
            raise TelegramConversationStateConsistencyError(
                "Versão conversacional persistida inconsistente."
            )

        return validated_saved

    def delete(
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

        deleted = delete_telegram_conversation_state(
            normalized_user_id,
            normalized_chat_id,
        )

        if not isinstance(
            deleted,
            bool,
        ):
            raise TelegramConversationStateConsistencyError(
                "Resultado de exclusão inconsistente."
            )

        return deleted

    def cleanup_expired(
        self,
        limit: int = 100,
    ) -> int:
        normalized_limit = validate_cleanup_limit(limit)

        deleted_count = delete_expired_telegram_conversation_states(normalized_limit)

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
            or deleted_count > normalized_limit
        ):
            raise TelegramConversationStateConsistencyError(
                "Resultado de limpeza inconsistente."
            )

        return deleted_count
