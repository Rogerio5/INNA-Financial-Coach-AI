from __future__ import annotations

from collections import Counter
from threading import RLock

from .contracts import (
    TelegramConversationMetricRecord,
)


class NoOpTelegramConversationMetrics:
    """
    Implementação padrão sem efeitos colaterais.
    """

    __slots__ = ()

    def record_operation(
        self,
        record: TelegramConversationMetricRecord,
    ) -> None:
        del record


class InMemoryTelegramConversationMetrics:
    """
    Coletor determinístico destinado a testes.

    Não realiza I/O e não depende de Prometheus.
    """

    def __init__(self) -> None:
        self._records: list[TelegramConversationMetricRecord] = []

        self._lock = RLock()

    def record_operation(
        self,
        record: TelegramConversationMetricRecord,
    ) -> None:
        if not isinstance(
            record,
            TelegramConversationMetricRecord,
        ):
            raise TypeError("record deve ser TelegramConversationMetricRecord.")

        with self._lock:
            self._records.append(record)

    def snapshot(
        self,
    ) -> tuple[
        TelegramConversationMetricRecord,
        ...,
    ]:
        with self._lock:
            return tuple(self._records)

    def clear(self) -> None:
        with self._lock:
            self._records.clear()

    def count(
        self,
        *,
        operation: str | None = None,
        component: str | None = None,
        outcome: str | None = None,
        error_category: str | None = None,
    ) -> int:
        return sum(
            1
            for record in self.snapshot()
            if (operation is None or record.operation == operation)
            and (component is None or record.component == component)
            and (outcome is None or record.outcome == outcome)
            and (error_category is None or record.error_category == error_category)
        )

    def operation_counts(
        self,
    ) -> dict[
        tuple[str, str, str],
        int,
    ]:
        counts = Counter(
            (
                record.component,
                record.operation,
                record.outcome,
            )
            for record in self.snapshot()
        )

        return dict(counts)

    def durations_ms(
        self,
        *,
        operation: str | None = None,
    ) -> tuple[float, ...]:
        return tuple(
            record.duration_ms
            for record in self.snapshot()
            if (operation is None or record.operation == operation)
        )
