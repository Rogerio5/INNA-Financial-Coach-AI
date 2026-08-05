from __future__ import annotations

from typing import Iterable, Protocol

from .contracts import (
    TelegramConversationMetricRecord,
)
from .productive_metrics import (
    TelegramProductiveMetricsSink,
)


class TelegramConversationMetricsRecorder(Protocol):
    def record_operation(
        self,
        metric: TelegramConversationMetricRecord,
    ) -> None: ...


class ProductiveTelegramConversationMetricsAdapter:
    """
    Adapta o contrato de métricas da bridge para
    o registry produtivo.

    A bridge continua emitindo um único registro.
    O adaptador converte esse registro nas famílias
    produtivas de counter e histogram.
    """

    def __init__(
        self,
        productive_metrics: TelegramProductiveMetricsSink,
    ) -> None:
        self._productive_metrics = productive_metrics

    def record_operation(
        self,
        metric: TelegramConversationMetricRecord,
    ) -> None:
        error_category = metric.error_category or "none"

        self._productive_metrics.increment(
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
            float(metric.duration_ms) / 1000.0,
        )

        self._productive_metrics.observe(
            ("inna_telegram_operation_duration_seconds"),
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
            self._productive_metrics.increment(
                "inna_telegram_failures_total",
                labels={
                    "component": metric.component,
                    "operation": metric.operation,
                    "error_category": error_category,
                },
            )

        if (
            metric.outcome
            in {
                "conflict",
                "recovered",
            }
            or metric.conflict_recovered is True
        ):
            conflict_outcome = (
                "recovered" if metric.conflict_recovered is True else metric.outcome
            )

            self._productive_metrics.increment(
                "inna_telegram_conflicts_total",
                labels={
                    "operation": metric.operation,
                    "outcome": conflict_outcome,
                },
            )


class CompositeTelegramConversationMetrics:
    """
    Encaminha um registro para múltiplos sinks.

    A falha de um sink não impede a execução
    dos demais e não quebra o fluxo produtivo.
    """

    def __init__(
        self,
        recorders: Iterable[TelegramConversationMetricsRecorder],
    ) -> None:
        self._recorders = tuple(recorders)

    def record_operation(
        self,
        metric: TelegramConversationMetricRecord,
    ) -> None:
        for recorder in self._recorders:
            try:
                recorder.record_operation(metric)
            except Exception:
                continue


__all__ = [
    "CompositeTelegramConversationMetrics",
    "ProductiveTelegramConversationMetricsAdapter",
    "TelegramConversationMetricsRecorder",
]
