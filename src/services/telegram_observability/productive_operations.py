from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .productive_metrics import (
    TelegramProductiveMetricsSink,
)


class TelegramProductiveOperations(Protocol):
    def record_worker_cycle(
        self,
        *,
        result: str,
    ) -> None: ...

    def record_worker_update(
        self,
        *,
        outcome: str,
        error_category: str | None = None,
    ) -> None: ...

    def record_receipt(
        self,
        *,
        status: str,
        outcome: str,
        error_category: str | None = None,
    ) -> None: ...

    def record_queue_operation(
        self,
        *,
        operation: str,
        outcome: str,
        error_category: str | None = None,
    ) -> None: ...


@dataclass(slots=True)
class TelegramProductiveOperationsRecorder:
    """
    API única para métricas produtivas específicas
    do worker, receipts e fila.

    Não recebe IDs, tokens, mensagens, payloads,
    estados financeiros ou exceções livres.
    """

    metrics: TelegramProductiveMetricsSink

    def record_worker_cycle(
        self,
        *,
        result: str,
    ) -> None:
        self.metrics.increment(
            "inna_telegram_worker_cycles_total",
            labels={
                "worker_result": result,
            },
        )

    def record_worker_update(
        self,
        *,
        outcome: str,
        error_category: str | None = None,
    ) -> None:
        resolved_error_category = error_category or "none"

        self.metrics.increment(
            "inna_telegram_worker_updates_total",
            labels={
                "outcome": outcome,
                "error_category": (resolved_error_category),
            },
        )

        if outcome in {
            "error",
            "conflict",
        }:
            self.metrics.increment(
                "inna_telegram_failures_total",
                labels={
                    "component": "worker",
                    "operation": "process_update",
                    "error_category": (resolved_error_category),
                },
            )

    def record_receipt(
        self,
        *,
        status: str,
        outcome: str,
        error_category: str | None = None,
    ) -> None:
        resolved_error_category = error_category or "none"

        self.metrics.increment(
            "inna_telegram_receipts_total",
            labels={
                "receipt_status": status,
                "outcome": outcome,
                "error_category": (resolved_error_category),
            },
        )

        if outcome in {
            "error",
            "conflict",
        }:
            operation = {
                "claimed": "claim_update",
                "completed": "complete_receipt",
                "failed": "fail_receipt",
            }.get(
                str(status).strip().lower(),
                "unknown",
            )

            self.metrics.increment(
                "inna_telegram_failures_total",
                labels={
                    "component": "receipt",
                    "operation": operation,
                    "error_category": (resolved_error_category),
                },
            )

    def record_queue_operation(
        self,
        *,
        operation: str,
        outcome: str,
        error_category: str | None = None,
    ) -> None:
        resolved_error_category = error_category or "none"

        self.metrics.increment(
            ("inna_telegram_queue_operations_total"),
            labels={
                "queue_operation": operation,
                "outcome": outcome,
                "error_category": (resolved_error_category),
            },
        )

        if outcome in {
            "error",
            "conflict",
        }:
            mapped_operation = {
                "enqueue": "enqueue_update",
                "claim": "dequeue_update",
                "acknowledge": "dequeue_update",
                "fail": "fail_receipt",
                "release": "dequeue_update",
                "recover": "dequeue_update",
            }.get(
                str(operation).strip().lower(),
                "unknown",
            )

            self.metrics.increment(
                "inna_telegram_failures_total",
                labels={
                    "component": "queue",
                    "operation": mapped_operation,
                    "error_category": (resolved_error_category),
                },
            )


class NoOpTelegramProductiveOperations:
    def record_worker_cycle(
        self,
        *,
        result: str,
    ) -> None:
        del result

    def record_worker_update(
        self,
        *,
        outcome: str,
        error_category: str | None = None,
    ) -> None:
        del outcome
        del error_category

    def record_receipt(
        self,
        *,
        status: str,
        outcome: str,
        error_category: str | None = None,
    ) -> None:
        del status
        del outcome
        del error_category

    def record_queue_operation(
        self,
        *,
        operation: str,
        outcome: str,
        error_category: str | None = None,
    ) -> None:
        del operation
        del outcome
        del error_category


class SafeTelegramProductiveOperations:
    """
    Impede que falhas da telemetria interrompam
    worker, receipts ou fila.
    """

    def __init__(
        self,
        delegate: TelegramProductiveOperations,
    ) -> None:
        self._delegate = delegate

    def record_worker_cycle(
        self,
        *,
        result: str,
    ) -> None:
        try:
            self._delegate.record_worker_cycle(
                result=result,
            )
        except Exception:
            return

    def record_worker_update(
        self,
        *,
        outcome: str,
        error_category: str | None = None,
    ) -> None:
        try:
            self._delegate.record_worker_update(
                outcome=outcome,
                error_category=error_category,
            )
        except Exception:
            return

    def record_receipt(
        self,
        *,
        status: str,
        outcome: str,
        error_category: str | None = None,
    ) -> None:
        try:
            self._delegate.record_receipt(
                status=status,
                outcome=outcome,
                error_category=error_category,
            )
        except Exception:
            return

    def record_queue_operation(
        self,
        *,
        operation: str,
        outcome: str,
        error_category: str | None = None,
    ) -> None:
        try:
            self._delegate.record_queue_operation(
                operation=operation,
                outcome=outcome,
                error_category=error_category,
            )
        except Exception:
            return


__all__ = [
    "NoOpTelegramProductiveOperations",
    "SafeTelegramProductiveOperations",
    "TelegramProductiveOperations",
    "TelegramProductiveOperationsRecorder",
]
