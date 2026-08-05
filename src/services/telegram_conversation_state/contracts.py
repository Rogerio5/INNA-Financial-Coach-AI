from __future__ import annotations

import json
import math
import re

from collections.abc import (
    Mapping,
    Sequence,
)
from copy import deepcopy
from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
    timezone,
)
from types import MappingProxyType
from typing import Any


MIN_STATE_TTL_SECONDS = 60

MAX_STATE_TTL_SECONDS = 30 * 24 * 60 * 60

DEFAULT_STATE_TTL_SECONDS = 24 * 60 * 60

MAX_STATE_JSON_BYTES = 32 * 1024

MAX_LANGUAGE_LENGTH = 16

MAX_CLEANUP_BATCH = 1_000


_LANGUAGE_PATTERN = re.compile(
    r"""
    [A-Za-z]{2,3}
    (?:
        [-_]
        [A-Za-z0-9]{2,8}
    ){0,2}
    """,
    re.VERBOSE,
)


class TelegramConversationStateError(RuntimeError):
    """
    Erro-base sanitizado do estado Telegram.
    """


class TelegramConversationStateValidationError(TelegramConversationStateError):
    """
    Entrada inválida ou fora do contrato.
    """


class TelegramConversationStateConflictError(TelegramConversationStateError):
    """
    Conflito de versão ou criação concorrente.
    """


class TelegramConversationStateConsistencyError(TelegramConversationStateError):
    """
    Estrutura persistida incompatível.
    """


class TelegramConversationStateUnavailableError(TelegramConversationStateError):
    """
    Persistência temporariamente indisponível.
    """


def _validation_error(
    message: str,
) -> TelegramConversationStateValidationError:
    return TelegramConversationStateValidationError(message)


def _validate_integer(
    value: Any,
    *,
    field_name: str,
    minimum: int | None = None,
    maximum: int | None = None,
    allow_zero: bool = True,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise _validation_error(f"{field_name} inválido.")

    if not allow_zero and value == 0:
        raise _validation_error(f"{field_name} inválido.")

    if minimum is not None and value < minimum:
        raise _validation_error(f"{field_name} inválido.")

    if maximum is not None and value > maximum:
        raise _validation_error(f"{field_name} inválido.")

    return value


def validate_telegram_identity(
    telegram_user_id: Any,
    chat_id: Any,
) -> tuple[int, int]:
    normalized_user_id = _validate_integer(
        telegram_user_id,
        field_name="telegram_user_id",
        minimum=1,
    )

    normalized_chat_id = _validate_integer(
        chat_id,
        field_name="chat_id",
        allow_zero=False,
    )

    return (
        normalized_user_id,
        normalized_chat_id,
    )


def normalize_telegram_language(
    language: Any,
) -> str | None:
    if language is None:
        return None

    if not isinstance(
        language,
        str,
    ):
        raise _validation_error("language inválido.")

    normalized = language.strip()

    if len(normalized) < 2 or len(normalized) > MAX_LANGUAGE_LENGTH:
        raise _validation_error("language inválido.")

    if _LANGUAGE_PATTERN.fullmatch(normalized) is None:
        raise _validation_error("language inválido.")

    return normalized


def _to_json_mutable(
    value: Any,
) -> Any:
    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        return value

    if isinstance(
        value,
        int,
    ):
        return value

    if isinstance(
        value,
        float,
    ):
        if not math.isfinite(value):
            raise _validation_error("state contém número inválido.")

        return value

    if isinstance(
        value,
        str,
    ):
        return value

    if isinstance(
        value,
        Mapping,
    ):
        normalized: dict[
            str,
            Any,
        ] = {}

        for key, nested_value in value.items():
            if not isinstance(
                key,
                str,
            ):
                raise _validation_error("state contém chave inválida.")

            normalized[key] = _to_json_mutable(nested_value)

        return normalized

    if isinstance(
        value,
        Sequence,
    ) and not isinstance(
        value,
        (
            str,
            bytes,
            bytearray,
        ),
    ):
        return [_to_json_mutable(item) for item in value]

    raise _validation_error("state contém valor inválido.")


def normalize_telegram_state(
    state: Any,
) -> dict[str, Any]:
    if not isinstance(
        state,
        Mapping,
    ):
        raise _validation_error("state deve ser um objeto JSON.")

    normalized = _to_json_mutable(state)

    if not isinstance(
        normalized,
        dict,
    ):
        raise _validation_error("state deve ser um objeto JSON.")

    try:
        serialized = json.dumps(
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
        raise _validation_error("state inválido.") from None

    encoded_size = len(serialized.encode("utf-8"))

    if encoded_size > MAX_STATE_JSON_BYTES:
        raise _validation_error("state excede o tamanho permitido.")

    try:
        round_trip = json.loads(serialized)

    except (
        TypeError,
        ValueError,
    ):
        raise _validation_error("state inválido.") from None

    if not isinstance(
        round_trip,
        dict,
    ):
        raise _validation_error("state deve ser um objeto JSON.")

    return round_trip


def validate_state_ttl_seconds(
    ttl_seconds: Any,
) -> int:
    return _validate_integer(
        ttl_seconds,
        field_name="ttl_seconds",
        minimum=(MIN_STATE_TTL_SECONDS),
        maximum=(MAX_STATE_TTL_SECONDS),
    )


def validate_expected_version(
    expected_version: Any,
) -> int:
    return _validate_integer(
        expected_version,
        field_name="expected_version",
        minimum=1,
    )


def validate_cleanup_limit(
    limit: Any,
) -> int:
    return _validate_integer(
        limit,
        field_name="limit",
        minimum=1,
        maximum=MAX_CLEANUP_BATCH,
    )


def _validate_datetime(
    value: Any,
    *,
    field_name: str,
) -> datetime:
    if not isinstance(
        value,
        datetime,
    ):
        raise _validation_error(f"{field_name} inválido.")

    if value.tzinfo is None or value.utcoffset() is None:
        raise _validation_error(f"{field_name} deve possuir timezone.")

    return value


def _freeze_json(
    value: Any,
) -> Any:
    if isinstance(
        value,
        dict,
    ):
        return MappingProxyType(
            {key: _freeze_json(nested_value) for key, nested_value in value.items()}
        )

    if isinstance(
        value,
        list,
    ):
        return tuple(_freeze_json(item) for item in value)

    return value


def _thaw_json(
    value: Any,
) -> Any:
    if isinstance(
        value,
        Mapping,
    ):
        return {key: _thaw_json(nested_value) for key, nested_value in value.items()}

    if isinstance(
        value,
        tuple,
    ):
        return [_thaw_json(item) for item in value]

    return deepcopy(value)


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramConversationState:
    telegram_user_id: int
    chat_id: int

    state: Mapping[
        str,
        Any,
    ] = field(repr=False)

    language: str | None

    state_version: int

    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    def __post_init__(
        self,
    ) -> None:
        (
            telegram_user_id,
            chat_id,
        ) = validate_telegram_identity(
            self.telegram_user_id,
            self.chat_id,
        )

        normalized_state = normalize_telegram_state(self.state)

        normalized_language = normalize_telegram_language(self.language)

        normalized_version = validate_expected_version(self.state_version)

        created_at = _validate_datetime(
            self.created_at,
            field_name="created_at",
        )

        updated_at = _validate_datetime(
            self.updated_at,
            field_name="updated_at",
        )

        expires_at = _validate_datetime(
            self.expires_at,
            field_name="expires_at",
        )

        if updated_at < created_at:
            raise _validation_error("updated_at não pode ser anterior a created_at.")

        if expires_at <= updated_at:
            raise _validation_error("expires_at deve ser posterior a updated_at.")

        object.__setattr__(
            self,
            "telegram_user_id",
            telegram_user_id,
        )

        object.__setattr__(
            self,
            "chat_id",
            chat_id,
        )

        object.__setattr__(
            self,
            "state",
            _freeze_json(normalized_state),
        )

        object.__setattr__(
            self,
            "language",
            normalized_language,
        )

        object.__setattr__(
            self,
            "state_version",
            normalized_version,
        )

        object.__setattr__(
            self,
            "created_at",
            created_at,
        )

        object.__setattr__(
            self,
            "updated_at",
            updated_at,
        )

        object.__setattr__(
            self,
            "expires_at",
            expires_at,
        )

    def to_processing_state(
        self,
    ) -> dict[str, Any]:
        mutable = _thaw_json(self.state)

        if not isinstance(
            mutable,
            dict,
        ):
            raise TelegramConversationStateConsistencyError(
                "Estado conversacional inconsistente."
            )

        return mutable

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "telegram_user_id": (self.telegram_user_id),
            "chat_id": self.chat_id,
            "language": self.language,
            "state_version": (self.state_version),
            "expires_at": (self.expires_at.isoformat()),
            "created_at": (self.created_at.isoformat()),
            "updated_at": (self.updated_at.isoformat()),
        }

    def is_expired(
        self,
        at: datetime | None = None,
    ) -> bool:
        reference = at if at is not None else datetime.now(timezone.utc)

        validated_reference = _validate_datetime(
            reference,
            field_name="at",
        )

        return self.expires_at <= validated_reference
