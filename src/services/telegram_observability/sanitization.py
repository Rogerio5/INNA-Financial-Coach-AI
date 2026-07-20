from __future__ import annotations

import math
import re
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import urlsplit


FORBIDDEN_OBSERVABILITY_FIELDS = frozenset(
    {
        "chat_id",
        "telegram_user_id",
        "session_id",
        "payload",
        "encrypted_payload",
        "decrypted_payload",
        "message_text",
        "text",
        "state",
        "financial_data",
        "nome",
        "renda",
        "renda_mensal",
        "gastos",
        "gastos_fixos",
        "gastos_variaveis",
        "dividas",
        "dividas_mensais",
        "reserva",
        "reserva_atual",
        "objetivo",
        "token",
        "secret",
        "password",
        "database_url",
        "configuration_value",
        "query",
        "parameters",
        "exception_message_raw",
    }
)

_ALLOWED_SCALAR_TYPES = (
    str,
    int,
    float,
    bool,
    type(None),
)

_MAX_STRING_LENGTH = 200

_DATABASE_URL_PATTERN = re.compile(
    r"(?i)"
    r"(?:postgres(?:ql)?|mysql|mariadb|mongodb"
    r"|redis|amqp|https?)://"
    r"[^\s]+"
)

_SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)"
    r"(token|secret|password|api[_-]?key)"
    r"\s*[:=]\s*"
    r"[^\s,;]+"
)

_BEARER_PATTERN = re.compile(
    r"\bBearer\s+[^\s,;]+",
    flags=re.IGNORECASE,
)

_LONG_CREDENTIAL_PATTERN = re.compile(
    r"[A-Za-z0-9_\-]{32,}"
)


def sanitize_error_category(
    value: object,
) -> str:
    normalized = str(
        value or "unknown"
    ).strip().lower()

    allowed = {
        "configuration",
        "validation",
        "security",
        "identity",
        "persistence",
        "external_service",
        "optimistic_conflict",
        "timeout",
        "unavailable",
        "unknown",
    }

    if normalized in allowed:
        return normalized

    return "unknown"


def _redact_string(
    value: str,
) -> str:
    sanitized = value

    sanitized = (
        _DATABASE_URL_PATTERN.sub(
            "[REDACTED_URL]",
            sanitized,
        )
    )

    sanitized = (
        _SECRET_ASSIGNMENT_PATTERN.sub(
            lambda match: (
                f"{match.group(1)}=[REDACTED]"
            ),
            sanitized,
        )
    )

    sanitized = (
        _BEARER_PATTERN.sub(
            "Bearer [REDACTED]",
            sanitized,
        )
    )

    sanitized = (
        _LONG_CREDENTIAL_PATTERN.sub(
            "[REDACTED_VALUE]",
            sanitized,
        )
    )

    if len(sanitized) > _MAX_STRING_LENGTH:
        sanitized = (
            sanitized[
                :_MAX_STRING_LENGTH
            ]
            + "..."
        )

    return sanitized


def sanitize_event_value(
    value: object,
) -> object:
    if isinstance(
        value,
        Path,
    ):
        return _redact_string(
            value.as_posix()
        )

    if isinstance(
        value,
        str,
    ):
        return _redact_string(value)

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
            return None

        return value

    if value is None:
        return None

    if isinstance(
        value,
        Mapping,
    ):
        return sanitize_event_fields(
            value
        )

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
            frozenset,
        ),
    ):
        return tuple(
            sanitize_event_value(item)
            for item in value
        )

    return _redact_string(
        type(value).__name__
    )


def sanitize_event_fields(
    fields: Mapping[str, object],
) -> dict[str, object]:
    sanitized: dict[
        str,
        object,
    ] = {}

    for raw_key, raw_value in fields.items():
        key = str(
            raw_key
        ).strip().lower()

        if not key:
            continue

        if key in FORBIDDEN_OBSERVABILITY_FIELDS:
            continue

        if any(
            forbidden in key
            for forbidden in (
                "token",
                "secret",
                "password",
                "credential",
                "payload",
                "financial",
            )
        ):
            continue

        sanitized[
            key
        ] = sanitize_event_value(
            raw_value
        )

    return sanitized
