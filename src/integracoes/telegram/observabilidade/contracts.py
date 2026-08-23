from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Protocol, runtime_checkable


ALLOWED_METRIC_OPERATIONS = frozenset(
    {
        "load_or_open_session",
        "save_session",
        "reload_session",
        "delete_session",
        "resolve_language",
        "claim_update",
        "process_update",
        "complete_receipt",
        "fail_receipt",
        "rollback",
    }
)

ALLOWED_METRIC_COMPONENTS = frozenset(
    {
        "bridge",
        "worker",
        "webhook",
        "receipt",
        "repository",
    }
)

ALLOWED_OUTCOMES = frozenset(
    {
        "success",
        "error",
        "conflict",
        "recovered",
        "discarded",
        "skipped",
    }
)

ALLOWED_ERROR_CATEGORIES = frozenset(
    {
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
)

ALLOWED_EVENT_LEVELS = frozenset(
    {
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    }
)


def _validate_choice(
    *,
    field_name: str,
    value: str,
    allowed: frozenset[str],
) -> str:
    normalized = str(value).strip().lower()

    if normalized not in allowed:
        raise ValueError(
            f"{field_name} inválido: {value!r}."
        )

    return normalized


def _validate_duration(
    value: float,
) -> float:
    duration = float(value)

    if duration < 0:
        raise ValueError(
            "duration_ms não pode ser negativa."
        )

    if duration != duration:
        raise ValueError(
            "duration_ms não pode ser NaN."
        )

    if duration in {
        float("inf"),
        float("-inf"),
    }:
        raise ValueError(
            "duration_ms deve ser finita."
        )

    return duration


@dataclass(
    frozen=True,
    slots=True,
)
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


@dataclass(
    frozen=True,
    slots=True,
)
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


@runtime_checkable
class TelegramConversationMetrics(
    Protocol
):
    def record_operation(
        self,
        record: TelegramConversationMetricRecord,
    ) -> None:
        """Registra uma operação observável."""


@runtime_checkable
class TelegramOperationalEventSink(
    Protocol
):
    def emit(
        self,
        event: TelegramOperationalEvent,
    ) -> None:
        """Emite um evento operacional sanitizado."""
