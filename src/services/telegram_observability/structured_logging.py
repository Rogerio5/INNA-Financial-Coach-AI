from __future__ import annotations

import json
import logging
import math

from collections.abc import (
    Callable,
    Mapping,
    Sequence,
)
from datetime import (
    date,
    datetime,
    timezone,
)
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .contracts import (
    TelegramOperationalEvent,
)
from .sanitization import (
    sanitize_event_fields,
)


_LEVEL_TO_LOGGING = MappingProxyType(
    {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
)

_MAX_NORMALIZATION_DEPTH = 8

_NON_SERIALIZABLE_MARKER = (
    "<non-serializable>"
)

_NON_FINITE_NUMBER_MARKER = (
    "<non-finite-number>"
)

_RECURSIVE_VALUE_MARKER = (
    "<recursive-value>"
)

_MAX_DEPTH_MARKER = (
    "<max-depth-exceeded>"
)


def telegram_structured_logging_utc_now(
) -> datetime:
    """
    Retorna o instante atual em UTC.

    A função é separada para permitir injeção
    determinística em testes.
    """
    return datetime.now(
        timezone.utc
    )


def format_telegram_log_timestamp(
    value: datetime,
) -> str:
    """
    Normaliza um datetime para ISO-8601 UTC
    com precisão de milissegundos e sufixo Z.
    """
    if not isinstance(
        value,
        datetime,
    ):
        raise TypeError(
            "clock deve retornar datetime."
        )

    if value.tzinfo is None:
        raise ValueError(
            "datetime do clock deve possuir timezone."
        )

    normalized = value.astimezone(
        timezone.utc
    )

    return (
        normalized.isoformat(
            timespec="milliseconds"
        )
        .replace(
            "+00:00",
            "Z",
        )
    )


def _safe_json_value(
    value: object,
    *,
    depth: int = 0,
    active_ids: set[int] | None = None,
) -> object:
    """
    Converte valores para uma estrutura JSON segura.

    A função nunca usa repr de objetos arbitrários,
    evitando vazamento acidental de segredos.
    """
    if depth > _MAX_NORMALIZATION_DEPTH:
        return _MAX_DEPTH_MARKER

    if active_ids is None:
        active_ids = set()

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
            return _NON_FINITE_NUMBER_MARKER

        return value

    if isinstance(
        value,
        str,
    ):
        return value

    if isinstance(
        value,
        datetime,
    ):
        if value.tzinfo is None:
            return value.isoformat(
                timespec="milliseconds"
            )

        return format_telegram_log_timestamp(
            value
        )

    if isinstance(
        value,
        date,
    ):
        return value.isoformat()

    if isinstance(
        value,
        Enum,
    ):
        return _safe_json_value(
            value.value,
            depth=depth + 1,
            active_ids=active_ids,
        )

    if isinstance(
        value,
        Path,
    ):
        return str(value)

    object_id = id(value)

    if object_id in active_ids:
        return _RECURSIVE_VALUE_MARKER

    if isinstance(
        value,
        Mapping,
    ):
        active_ids.add(
            object_id
        )

        try:
            normalized = {}

            for raw_key, raw_value in (
                value.items()
            ):
                key = str(
                    raw_key
                )

                normalized[key] = (
                    _safe_json_value(
                        raw_value,
                        depth=depth + 1,
                        active_ids=active_ids,
                    )
                )

            return normalized

        finally:
            active_ids.discard(
                object_id
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
        active_ids.add(
            object_id
        )

        try:
            items = [
                _safe_json_value(
                    item,
                    depth=depth + 1,
                    active_ids=active_ids,
                )
                for item in value
            ]

            if isinstance(
                value,
                (
                    set,
                    frozenset,
                ),
            ):
                return sorted(
                    items,
                    key=lambda item: json.dumps(
                        item,
                        ensure_ascii=False,
                        sort_keys=True,
                        allow_nan=False,
                    ),
                )

            return items

        finally:
            active_ids.discard(
                object_id
            )

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
        active_ids.add(
            object_id
        )

        try:
            return [
                _safe_json_value(
                    item,
                    depth=depth + 1,
                    active_ids=active_ids,
                )
                for item in value
            ]

        finally:
            active_ids.discard(
                object_id
            )

    return _NON_SERIALIZABLE_MARKER


def build_telegram_structured_log_payload(
    event: TelegramOperationalEvent,
    *,
    timestamp: datetime,
) -> dict[str, object]:
    """
    Constrói o payload canônico e sanitizado.
    """
    if not isinstance(
        event,
        TelegramOperationalEvent,
    ):
        raise TypeError(
            "event deve ser TelegramOperationalEvent."
        )

    normalized_fields = (
        _safe_json_value(
            event.fields
        )
    )

    if not isinstance(
        normalized_fields,
        dict,
    ):
        normalized_fields = {}

    safe_fields = sanitize_event_fields(
        normalized_fields
    )

    if not isinstance(
        safe_fields,
        dict,
    ):
        safe_fields = {}

    return {
        "timestamp": (
            format_telegram_log_timestamp(
                timestamp
            )
        ),
        "level": event.level,
        "event": event.name,
        "component": event.component,
        "outcome": event.outcome,
        "fields": safe_fields,
    }


def serialize_telegram_structured_log(
    event: TelegramOperationalEvent,
    *,
    timestamp: datetime,
) -> str:
    """
    Serializa exatamente uma linha JSON.
    """
    payload = (
        build_telegram_structured_log_payload(
            event,
            timestamp=timestamp,
        )
    )

    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )

    if (
        "\n" in serialized
        or "\r" in serialized
    ):
        raise ValueError(
            "O log estruturado deve ocupar uma única linha."
        )

    return serialized


class JsonTelegramOperationalEventSink:
    """
    Emite TelegramOperationalEvent por logging.Logger.

    A mensagem enviada ao logger é uma única linha
    JSON pronta para ingestão por ferramentas externas.
    """

    __slots__ = (
        "_logger",
        "_clock",
    )

    def __init__(
        self,
        *,
        logger: logging.Logger,
        clock: Callable[
            [],
            datetime,
        ] = telegram_structured_logging_utc_now,
    ) -> None:
        if not isinstance(
            logger,
            logging.Logger,
        ):
            raise TypeError(
                "logger deve ser logging.Logger."
            )

        if not callable(clock):
            raise TypeError(
                "clock deve ser callable."
            )

        self._logger = logger
        self._clock = clock

    @property
    def logger(
        self,
    ) -> logging.Logger:
        return self._logger

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

        timestamp = self._clock()

        serialized = (
            serialize_telegram_structured_log(
                event,
                timestamp=timestamp,
            )
        )

        level = _LEVEL_TO_LOGGING[
            event.level
        ]

        self._logger.log(
            level,
            serialized,
        )
