from __future__ import annotations

from collections.abc import Mapping
from dataclasses import (
    dataclass,
    field,
)
from typing import Any

from .contracts import (
    DEFAULT_STATE_TTL_SECONDS,
    TelegramConversationState,
    TelegramConversationStateConsistencyError,
    TelegramConversationStateValidationError,
    normalize_telegram_language,
    normalize_telegram_state,
    validate_cleanup_limit,
    validate_state_ttl_seconds,
    validate_telegram_identity,
)

from .store import (
    PostgresTelegramConversationStateStore,
    TelegramConversationStateOpenResult,
    TelegramConversationStateStore,
)


@dataclass(
    slots=True,
)
class TelegramConversationSession:
    current: TelegramConversationState = field(
        repr=False
    )

    state: dict[str, Any] = field(
        repr=False
    )

    language: str | None = None

    created: bool = False

    recovered_from_conflict: bool = False

    deleted: bool = False

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

    @property
    def telegram_user_id(
        self,
    ) -> int:
        return self.current.telegram_user_id

    @property
    def chat_id(
        self,
    ) -> int:
        return self.current.chat_id

    @property
    def state_version(
        self,
    ) -> int:
        return self.current.state_version

    def replace_state(
        self,
        state: Mapping[str, Any],
    ) -> None:
        self._require_active()

        self.state = normalize_telegram_state(
            state
        )

    def set_language(
        self,
        language: str | None,
    ) -> None:
        self._require_active()

        self.language = (
            normalize_telegram_language(
                language
            )
        )

    def reset_to_persisted(
        self,
    ) -> None:
        self._require_active()

        self.state = (
            self.current.to_processing_state()
        )

        self.language = (
            self.current.language
        )

    def is_dirty(
        self,
    ) -> bool:
        self._require_active()

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

        return (
            normalized_state
            != self.current.to_processing_state()
            or normalized_language
            != self.current.language
        )

    def to_processing_state(
        self,
    ) -> dict[str, Any]:
        self._require_active()

        return normalize_telegram_state(
            self.state
        )

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

    def _require_active(
        self,
    ) -> None:
        if self.deleted:
            raise TelegramConversationStateValidationError(
                "Sessão conversacional já removida."
            )


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


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramConversationStateRuntime:
    store: TelegramConversationStateStore = field(
        repr=False
    )

    default_ttl_seconds: int = (
        DEFAULT_STATE_TTL_SECONDS
    )

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.store,
            TelegramConversationStateStore,
        ):
            raise TelegramConversationStateValidationError(
                "store inválido."
            )

        validated_ttl = (
            validate_state_ttl_seconds(
                self.default_ttl_seconds
            )
        )

        object.__setattr__(
            self,
            "default_ttl_seconds",
            validated_ttl,
        )

    def _resolve_ttl(
        self,
        ttl_seconds: int | None,
    ) -> int:
        if ttl_seconds is None:
            return self.default_ttl_seconds

        return validate_state_ttl_seconds(
            ttl_seconds
        )

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

        record = self.store.load(
            normalized_user_id,
            normalized_chat_id,
        )

        if record is None:
            return None

        return _session_from_record(
            record
        )

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

    def delete_session(
        self,
        session: TelegramConversationSession,
    ) -> bool:
        validated_session = (
            self._require_session(
                session
            )
        )

        deleted = self.store.delete(
            validated_session.telegram_user_id,
            validated_session.chat_id,
        )

        if not isinstance(
            deleted,
            bool,
        ):
            raise TelegramConversationStateConsistencyError(
                "Resultado de exclusão inválido."
            )

        validated_session.deleted = True

        return deleted

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

        deleted = self.store.delete(
            normalized_user_id,
            normalized_chat_id,
        )

        if not isinstance(
            deleted,
            bool,
        ):
            raise TelegramConversationStateConsistencyError(
                "Resultado de exclusão inválido."
            )

        return deleted

    def cleanup_expired(
        self,
        limit: int = 100,
    ) -> int:
        normalized_limit = (
            validate_cleanup_limit(
                limit
            )
        )

        deleted_count = (
            self.store.cleanup_expired(
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
                "Resultado de cleanup inválido."
            )

        return deleted_count

    @staticmethod
    def _require_session(
        session: Any,
    ) -> TelegramConversationSession:
        if not isinstance(
            session,
            TelegramConversationSession,
        ):
            raise TelegramConversationStateValidationError(
                "session inválida."
            )

        session._require_active()

        return session


def create_postgres_telegram_conversation_state_runtime(
    *,
    default_ttl_seconds: int = (
        DEFAULT_STATE_TTL_SECONDS
    ),
) -> TelegramConversationStateRuntime:
    validated_ttl = (
        validate_state_ttl_seconds(
            default_ttl_seconds
        )
    )

    store = (
        PostgresTelegramConversationStateStore()
    )

    return TelegramConversationStateRuntime(
        store=store,
        default_ttl_seconds=validated_ttl,
    )
