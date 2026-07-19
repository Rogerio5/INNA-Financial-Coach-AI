from __future__ import annotations

import json

from collections.abc import (
    Mapping,
)
from datetime import datetime
from typing import Any

from src.database.connection import (
    cursor_postgres,
)

from .contracts import (
    DEFAULT_STATE_TTL_SECONDS,
    TelegramConversationState,
    TelegramConversationStateConflictError,
    TelegramConversationStateConsistencyError,
    TelegramConversationStateError,
    TelegramConversationStateUnavailableError,
    TelegramConversationStateValidationError,
    normalize_telegram_language,
    normalize_telegram_state,
    validate_cleanup_limit,
    validate_expected_version,
    validate_state_ttl_seconds,
    validate_telegram_identity,
)


_LOAD_STATE_SQL = """
SELECT
    telegram_user_id,
    chat_id,
    state,
    language,
    state_version,
    expires_at,
    created_at,
    updated_at

FROM
    public.telegram_conversation_states

WHERE telegram_user_id = %s
  AND chat_id = %s
  AND expires_at > CURRENT_TIMESTAMP

LIMIT 1;
"""


_CREATE_STATE_SQL = """
INSERT INTO
    public.telegram_conversation_states
(
    telegram_user_id,
    chat_id,
    state,
    language,
    expires_at
)
VALUES
(
    %s,
    %s,
    %s::jsonb,
    %s,
    CURRENT_TIMESTAMP
        + (%s * INTERVAL '1 second')
)

ON CONFLICT
(
    telegram_user_id,
    chat_id
)
DO UPDATE

SET
    state = EXCLUDED.state,
    language = EXCLUDED.language,
    state_version =
        public.telegram_conversation_states
        .state_version + 1,
    updated_at = CURRENT_TIMESTAMP,
    expires_at = EXCLUDED.expires_at

WHERE
    public.telegram_conversation_states
    .expires_at <= CURRENT_TIMESTAMP

RETURNING
    telegram_user_id,
    chat_id,
    state,
    language,
    state_version,
    expires_at,
    created_at,
    updated_at;
"""


_SAVE_STATE_SQL = """
UPDATE
    public.telegram_conversation_states

SET
    state = %s::jsonb,
    language = %s,
    state_version =
        state_version + 1,
    updated_at = CURRENT_TIMESTAMP,
    expires_at =
        CURRENT_TIMESTAMP
        + (%s * INTERVAL '1 second')

WHERE telegram_user_id = %s
  AND chat_id = %s
  AND state_version = %s
  AND expires_at > CURRENT_TIMESTAMP

RETURNING
    telegram_user_id,
    chat_id,
    state,
    language,
    state_version,
    expires_at,
    created_at,
    updated_at;
"""


_DELETE_STATE_SQL = """
DELETE FROM
    public.telegram_conversation_states

WHERE telegram_user_id = %s
  AND chat_id = %s

RETURNING
    telegram_user_id;
"""


_DELETE_EXPIRED_STATES_SQL = """
WITH expired_states AS
(
    SELECT
        telegram_user_id,
        chat_id

    FROM
        public.telegram_conversation_states

    WHERE expires_at
        <= CURRENT_TIMESTAMP

    ORDER BY
        expires_at ASC,
        telegram_user_id ASC,
        chat_id ASC

    LIMIT %s

    FOR UPDATE
        SKIP LOCKED
)

DELETE FROM
    public.telegram_conversation_states
    AS conversation_state

USING
    expired_states

WHERE
    conversation_state.telegram_user_id =
        expired_states.telegram_user_id

AND
    conversation_state.chat_id =
        expired_states.chat_id

RETURNING
    conversation_state.telegram_user_id,
    conversation_state.chat_id;
"""


def _serialize_state(
    state: Mapping[str, Any],
) -> str:
    normalized = normalize_telegram_state(
        state
    )

    try:
        return json.dumps(
            normalized,
            ensure_ascii=False,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            allow_nan=False,
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
        RecursionError,
    ):
        raise TelegramConversationStateValidationError(
            "state inválido."
        ) from None


def _deserialize_state(
    raw_state: Any,
) -> dict[str, Any]:
    candidate = raw_state

    if isinstance(
        candidate,
        memoryview,
    ):
        candidate = candidate.tobytes()

    if isinstance(
        candidate,
        (
            bytes,
            bytearray,
        ),
    ):
        try:
            candidate = bytes(
                candidate
            ).decode(
                "utf-8"
            )

        except UnicodeDecodeError:
            raise TelegramConversationStateConsistencyError(
                "Estado conversacional persistido inválido."
            ) from None

    if isinstance(
        candidate,
        str,
    ):
        try:
            candidate = json.loads(
                candidate
            )

        except (
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ):
            raise TelegramConversationStateConsistencyError(
                "Estado conversacional persistido inválido."
            ) from None

    try:
        return normalize_telegram_state(
            candidate
        )

    except TelegramConversationStateValidationError:
        raise TelegramConversationStateConsistencyError(
            "Estado conversacional persistido inválido."
        ) from None


def _record_from_row(
    row: Any,
    *,
    expected_telegram_user_id: int | None = None,
    expected_chat_id: int | None = None,
) -> TelegramConversationState:
    if not isinstance(
        row,
        Mapping,
    ):
        raise TelegramConversationStateConsistencyError(
            "Registro conversacional persistido inválido."
        )

    try:
        telegram_user_id = row[
            "telegram_user_id"
        ]

        chat_id = row[
            "chat_id"
        ]

        state = _deserialize_state(
            row["state"]
        )

        language = row[
            "language"
        ]

        state_version = row[
            "state_version"
        ]

        expires_at = row[
            "expires_at"
        ]

        created_at = row[
            "created_at"
        ]

        updated_at = row[
            "updated_at"
        ]

    except (
        KeyError,
        TypeError,
    ):
        raise TelegramConversationStateConsistencyError(
            "Registro conversacional persistido incompleto."
        ) from None

    try:
        record = TelegramConversationState(
            telegram_user_id=(
                telegram_user_id
            ),
            chat_id=chat_id,
            state=state,
            language=language,
            state_version=state_version,
            expires_at=expires_at,
            created_at=created_at,
            updated_at=updated_at,
        )

    except TelegramConversationStateValidationError:
        raise TelegramConversationStateConsistencyError(
            "Registro conversacional persistido incompatível."
        ) from None

    if (
        expected_telegram_user_id
        is not None
        and record.telegram_user_id
        != expected_telegram_user_id
    ):
        raise TelegramConversationStateConsistencyError(
            "Identidade persistida inconsistente."
        )

    if (
        expected_chat_id is not None
        and record.chat_id
        != expected_chat_id
    ):
        raise TelegramConversationStateConsistencyError(
            "Escopo persistido inconsistente."
        )

    return record


def _require_connection(
    cursor: Any,
) -> Any:
    connection = getattr(
        cursor,
        "connection",
        None,
    )

    if connection is None:
        raise TelegramConversationStateUnavailableError(
            "Persistência conversacional indisponível."
        )

    return connection


def _safe_rollback(
    connection: Any,
) -> None:
    try:
        connection.rollback()

    except Exception:
        pass


def _raise_unavailable() -> None:
    raise TelegramConversationStateUnavailableError(
        "Persistência conversacional temporariamente indisponível."
    ) from None


def load_telegram_conversation_state(
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
                    _LOAD_STATE_SQL,
                    (
                        normalized_user_id,
                        normalized_chat_id,
                    ),
                )

                row = cursor.fetchone()

                connection.rollback()

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

    if row is None:
        return None

    return _record_from_row(
        row,
        expected_telegram_user_id=(
            normalized_user_id
        ),
        expected_chat_id=(
            normalized_chat_id
        ),
    )


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


def delete_telegram_conversation_state(
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
                    _DELETE_STATE_SQL,
                    (
                        normalized_user_id,
                        normalized_chat_id,
                    ),
                )

                deleted_row = (
                    cursor.fetchone()
                )

                connection.commit()

                return (
                    deleted_row
                    is not None
                )

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


def delete_expired_telegram_conversation_states(
    limit: int = 100,
) -> int:
    normalized_limit = (
        validate_cleanup_limit(
            limit
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
                    _DELETE_EXPIRED_STATES_SQL,
                    (
                        normalized_limit,
                    ),
                )

                deleted_rows = list(
                    cursor.fetchall()
                )

                connection.commit()

                return len(
                    deleted_rows
                )

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
