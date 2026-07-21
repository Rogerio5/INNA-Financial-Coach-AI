from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import isfinite
from threading import RLock
from types import MappingProxyType
from typing import Mapping, Protocol

from .contracts import (
    TelegramConversationMetricRecord,
)


TELEGRAM_OPERATION_DURATION_BUCKETS_SECONDS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
    30.0,
)


_ALLOWED_LABEL_VALUES = MappingProxyType(
    {
        "component": frozenset(
            {
                "webhook",
                "worker",
                "bridge",
                "receipt",
                "queue",
                "repository",
                "unknown",
            }
        ),
        "operation": frozenset(
            {
                "process_update",
                "claim_update",
                "complete_receipt",
                "fail_receipt",
                "enqueue_update",
                "dequeue_update",
                "load_or_open_session",
                "save_session",
                "reload_session",
                "delete_session",
                "resolve_language",
                "worker_cycle",
                "unknown",
            }
        ),
        "outcome": frozenset(
            {
                "success",
                "error",
                "conflict",
                "recovered",
                "discarded",
                "duplicate",
                "skipped",
                "empty",
                "unknown",
            }
        ),
        "error_category": frozenset(
            {
                "none",
                "validation",
                "configuration",
                "persistence",
                "optimistic_conflict",
                "encryption",
                "delivery",
                "timeout",
                "dependency",
                "unknown",
            }
        ),
        "receipt_status": frozenset(
            {
                "claimed",
                "completed",
                "failed",
                "duplicate",
                "expired",
                "released",
                "unknown",
            }
        ),
        "queue_operation": frozenset(
            {
                "enqueue",
                "claim",
                "acknowledge",
                "fail",
                "release",
                "recover",
                "unknown",
            }
        ),
        "worker_result": frozenset(
            {
                "processed",
                "failed",
                "empty",
                "stopped",
                "max_cycles",
                "unknown",
            }
        ),
    }
)


_FORBIDDEN_LABEL_NAMES = frozenset(
    {
        "user_id",
        "telegram_user_id",
        "chat_id",
        "update_id",
        "message_id",
        "receipt_id",
        "claim_token",
        "lease_token",
        "session_id",
        "username",
        "name",
        "email",
        "phone",
        "language_text",
        "message_text",
        "payload",
        "processing_state",
        "financial_data",
        "income",
        "expenses",
        "debt",
        "score",
        "token",
        "secret",
        "password",
        "authorization",
        "database_url",
        "exception",
        "exception_message",
        "traceback",
    }
)


_METRIC_LABELS = MappingProxyType(
    {
        "inna_telegram_operations_total": (
            "component",
            "operation",
            "outcome",
            "error_category",
        ),
        "inna_telegram_operation_duration_seconds": (
            "component",
            "operation",
            "outcome",
        ),
        "inna_telegram_conflicts_total": (
            "operation",
            "outcome",
        ),
        "inna_telegram_receipts_total": (
            "receipt_status",
            "outcome",
            "error_category",
        ),
        "inna_telegram_worker_cycles_total": (
            "worker_result",
        ),
        "inna_telegram_worker_updates_total": (
            "outcome",
            "error_category",
        ),
        "inna_telegram_queue_operations_total": (
            "queue_operation",
            "outcome",
            "error_category",
        ),
        "inna_telegram_failures_total": (
            "component",
            "operation",
            "error_category",
        ),
    }
)


def _normalize_label_name(
    name: object,
) -> str:
    normalized = str(
        name
    ).strip().lower()

    if not normalized:
        raise ValueError(
            "Nome de label vazio."
        )

    if normalized in _FORBIDDEN_LABEL_NAMES:
        raise ValueError(
            "Label proibida."
        )

    if normalized not in _ALLOWED_LABEL_VALUES:
        raise ValueError(
            "Label não registrada."
        )

    return normalized


def _normalize_label_value(
    *,
    label: str,
    value: object,
) -> str:
    allowed = _ALLOWED_LABEL_VALUES[
        label
    ]

    if value is None:
        candidate = (
            "none"
            if label == "error_category"
            else "unknown"
        )
    else:
        candidate = str(
            value
        ).strip().lower()

    if candidate in allowed:
        return candidate

    if "unknown" in allowed:
        return "unknown"

    raise ValueError(
        f"Valor inválido para label {label!r}."
    )


def normalize_metric_labels(
    *,
    metric_name: str,
    labels: Mapping[str, object],
) -> tuple[tuple[str, str], ...]:
    expected = _METRIC_LABELS.get(
        metric_name
    )

    if expected is None:
        raise ValueError(
            "Família de métrica não registrada."
        )

    provided_names = {
        _normalize_label_name(name)
        for name in labels
    }

    expected_names = set(
        expected
    )

    if provided_names != expected_names:
        missing = sorted(
            expected_names
            - provided_names
        )

        unexpected = sorted(
            provided_names
            - expected_names
        )

        raise ValueError(
            "Conjunto de labels inválido. "
            f"Ausentes={missing}, "
            f"inesperadas={unexpected}."
        )

    normalized = []

    for name in expected:
        normalized.append(
            (
                name,
                _normalize_label_value(
                    label=name,
                    value=labels[name],
                ),
            )
        )

    return tuple(
        normalized
    )


@dataclass(frozen=True, slots=True)
class TelegramHistogramSnapshot:
    count: int
    sum: float
    buckets: Mapping[float, int]


@dataclass(frozen=True, slots=True)
class TelegramProductiveMetricsSnapshot:
    counters: Mapping[
        str,
        Mapping[
            tuple[tuple[str, str], ...],
            float,
        ],
    ]
    histograms: Mapping[
        str,
        Mapping[
            tuple[tuple[str, str], ...],
            TelegramHistogramSnapshot,
        ],
    ]


class TelegramProductiveMetricsSink(
    Protocol
):
    def increment(
        self,
        metric_name: str,
        *,
        labels: Mapping[str, object],
        value: float = 1.0,
    ) -> None:
        ...

    def observe(
        self,
        metric_name: str,
        value: float,
        *,
        labels: Mapping[str, object],
    ) -> None:
        ...


class NoOpTelegramProductiveMetrics:
    def increment(
        self,
        metric_name: str,
        *,
        labels: Mapping[str, object],
        value: float = 1.0,
    ) -> None:
        del metric_name
        del labels
        del value

    def observe(
        self,
        metric_name: str,
        value: float,
        *,
        labels: Mapping[str, object],
    ) -> None:
        del metric_name
        del value
        del labels


class InMemoryTelegramProductiveMetrics:
    def __init__(
        self,
        *,
        histogram_buckets: tuple[
            float,
            ...
        ] = TELEGRAM_OPERATION_DURATION_BUCKETS_SECONDS,
    ) -> None:
        normalized_buckets = tuple(
            sorted(
                float(bucket)
                for bucket in histogram_buckets
            )
        )

        if not normalized_buckets:
            raise ValueError(
                "Histogram precisa de buckets."
            )

        if any(
            not isfinite(bucket)
            or bucket <= 0
            for bucket in normalized_buckets
        ):
            raise ValueError(
                "Buckets precisam ser finitos e positivos."
            )

        if len(
            normalized_buckets
        ) != len(
            set(normalized_buckets)
        ):
            raise ValueError(
                "Buckets duplicados."
            )

        self._histogram_buckets = (
            normalized_buckets
        )

        self._counter_values = defaultdict(
            float
        )

        self._histogram_counts = defaultdict(
            int
        )

        self._histogram_sums = defaultdict(
            float
        )

        self._histogram_bucket_counts = (
            defaultdict(int)
        )

        self._lock = RLock()

    def increment(
        self,
        metric_name: str,
        *,
        labels: Mapping[str, object],
        value: float = 1.0,
    ) -> None:
        numeric_value = float(
            value
        )

        if (
            not isfinite(numeric_value)
            or numeric_value < 0
        ):
            raise ValueError(
                "Incremento precisa ser finito e não negativo."
            )

        if metric_name == (
            "inna_telegram_operation_duration_seconds"
        ):
            raise ValueError(
                "Histogram deve usar observe()."
            )

        normalized_labels = (
            normalize_metric_labels(
                metric_name=metric_name,
                labels=labels,
            )
        )

        key = (
            metric_name,
            normalized_labels,
        )

        with self._lock:
            self._counter_values[
                key
            ] += numeric_value

    def observe(
        self,
        metric_name: str,
        value: float,
        *,
        labels: Mapping[str, object],
    ) -> None:
        if metric_name != (
            "inna_telegram_operation_duration_seconds"
        ):
            raise ValueError(
                "observe() aceita apenas histogramas."
            )

        numeric_value = float(
            value
        )

        if (
            not isfinite(numeric_value)
            or numeric_value < 0
        ):
            raise ValueError(
                "Observação precisa ser finita e não negativa."
            )

        normalized_labels = (
            normalize_metric_labels(
                metric_name=metric_name,
                labels=labels,
            )
        )

        key = (
            metric_name,
            normalized_labels,
        )

        with self._lock:
            self._histogram_counts[
                key
            ] += 1

            self._histogram_sums[
                key
            ] += numeric_value

            for bucket in (
                self._histogram_buckets
            ):
                if numeric_value <= bucket:
                    self._histogram_bucket_counts[
                        (
                            metric_name,
                            normalized_labels,
                            bucket,
                        )
                    ] += 1

    def record_conversation_operation(
        self,
        metric: TelegramConversationMetricRecord,
    ) -> None:
        error_category = (
            metric.error_category
            or "none"
        )

        self.increment(
            "inna_telegram_operations_total",
            labels={
                "component": metric.component,
                "operation": metric.operation,
                "outcome": metric.outcome,
                "error_category": error_category,
            },
        )

        duration_seconds = max(
            0.0,
            float(
                metric.duration_ms
            )
            / 1000.0,
        )

        self.observe(
            (
                "inna_telegram_"
                "operation_duration_seconds"
            ),
            duration_seconds,
            labels={
                "component": metric.component,
                "operation": metric.operation,
                "outcome": metric.outcome,
            },
        )

        if metric.outcome in {
            "error",
            "conflict",
        }:
            self.increment(
                "inna_telegram_failures_total",
                labels={
                    "component": metric.component,
                    "operation": metric.operation,
                    "error_category": (
                        error_category
                    ),
                },
            )

        if (
            metric.outcome
            in {
                "conflict",
                "recovered",
            }
            or metric.conflict_recovered
            is True
        ):
            conflict_outcome = (
                "recovered"
                if metric.conflict_recovered
                is True
                else metric.outcome
            )

            self.increment(
                "inna_telegram_conflicts_total",
                labels={
                    "operation": metric.operation,
                    "outcome": conflict_outcome,
                },
            )

    def snapshot(
        self,
    ) -> TelegramProductiveMetricsSnapshot:
        with self._lock:
            counters_by_metric = {}

            for (
                metric_name,
                labels,
            ), value in (
                self._counter_values.items()
            ):
                counters_by_metric.setdefault(
                    metric_name,
                    {},
                )[labels] = value

            histograms_by_metric = {}

            for (
                metric_name,
                labels,
            ), count in (
                self._histogram_counts.items()
            ):
                buckets = {
                    bucket: (
                        self._histogram_bucket_counts[
                            (
                                metric_name,
                                labels,
                                bucket,
                            )
                        ]
                    )
                    for bucket in (
                        self._histogram_buckets
                    )
                }

                histogram = (
                    TelegramHistogramSnapshot(
                        count=count,
                        sum=(
                            self._histogram_sums[
                                (
                                    metric_name,
                                    labels,
                                )
                            ]
                        ),
                        buckets=MappingProxyType(
                            buckets
                        ),
                    )
                )

                histograms_by_metric.setdefault(
                    metric_name,
                    {},
                )[labels] = histogram

            immutable_counters = MappingProxyType(
                {
                    name: MappingProxyType(
                        values.copy()
                    )
                    for name, values in (
                        counters_by_metric.items()
                    )
                }
            )

            immutable_histograms = MappingProxyType(
                {
                    name: MappingProxyType(
                        values.copy()
                    )
                    for name, values in (
                        histograms_by_metric.items()
                    )
                }
            )

            return (
                TelegramProductiveMetricsSnapshot(
                    counters=immutable_counters,
                    histograms=(
                        immutable_histograms
                    ),
                )
            )

    def reset(
        self,
    ) -> None:
        with self._lock:
            self._counter_values.clear()
            self._histogram_counts.clear()
            self._histogram_sums.clear()
            self._histogram_bucket_counts.clear()


class SafeTelegramProductiveMetrics:
    def __init__(
        self,
        delegate: TelegramProductiveMetricsSink,
    ) -> None:
        self._delegate = delegate

    def increment(
        self,
        metric_name: str,
        *,
        labels: Mapping[str, object],
        value: float = 1.0,
    ) -> None:
        try:
            self._delegate.increment(
                metric_name,
                labels=labels,
                value=value,
            )
        except Exception:
            return

    def observe(
        self,
        metric_name: str,
        value: float,
        *,
        labels: Mapping[str, object],
    ) -> None:
        try:
            self._delegate.observe(
                metric_name,
                value,
                labels=labels,
            )
        except Exception:
            return


__all__ = [
    "InMemoryTelegramProductiveMetrics",
    "NoOpTelegramProductiveMetrics",
    "SafeTelegramProductiveMetrics",
    "TELEGRAM_OPERATION_DURATION_BUCKETS_SECONDS",
    "TelegramHistogramSnapshot",
    "TelegramProductiveMetricsSink",
    "TelegramProductiveMetricsSnapshot",
    "normalize_metric_labels",
]
