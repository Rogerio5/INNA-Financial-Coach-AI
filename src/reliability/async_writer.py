"""Writer assíncrono do Reliability Ledger da INNA."""

from __future__ import annotations

import math
import os
import queue
import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from src.resilience.events import (
    ResilienceEvent,
    ResilienceEventType,
)

from .production_tracker import (
    PRODUCTION_RELIABILITY_POLICIES,
)
from .repository import (
    ProductionReliabilityLedgerWrite,
    initialize_production_reliability_schema,
    persist_production_reliability_event,
)

_TERMINAL_EVENT_TYPES = frozenset(
    {
        ResilienceEventType.OPERATION_SUCCEEDED,
        ResilienceEventType.OPERATION_FAILED,
        ResilienceEventType.CIRCUIT_REJECTED,
    }
)


def _env_bool(
    name: str,
    *,
    default: bool,
) -> bool:
    raw = os.getenv(name)

    if raw is None:
        return default

    normalized = raw.strip().lower()

    if normalized in {
        "1",
        "true",
        "yes",
        "on",
    }:
        return True

    if normalized in {
        "0",
        "false",
        "no",
        "off",
    }:
        return False

    return default


def _env_positive_int(
    name: str,
    *,
    default: int,
) -> int:
    raw = os.getenv(name)

    if raw is None:
        return default

    try:
        parsed = int(raw)
    except ValueError:
        return default

    if parsed < 1:
        return default

    return parsed


def _env_nonnegative_float(
    name: str,
    *,
    default: float,
) -> float:
    raw = os.getenv(name)

    if raw is None:
        return default

    try:
        parsed = float(raw)
    except ValueError:
        return default

    if (
        not math.isfinite(parsed)
        or parsed < 0
    ):
        return default

    return parsed


@dataclass(
    frozen=True,
    slots=True,
)
class ProductionReliabilityWriterSnapshot:
    enabled: bool
    worker_running: bool

    queue_capacity: int
    pending_events: int

    enqueued_events: int
    persisted_events: int
    duplicate_events: int

    persistence_failures: int
    retry_attempts: int
    queue_full_drops: int

    ignored_nonterminal_events: int
    ignored_untracked_events: int

    worker_starts: int

    def to_safe_dict(
        self,
    ) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "enabled": self.enabled,
                "worker_running": (
                    self.worker_running
                ),
                "queue_capacity": (
                    self.queue_capacity
                ),
                "pending_events": (
                    self.pending_events
                ),
                "enqueued_events": (
                    self.enqueued_events
                ),
                "persisted_events": (
                    self.persisted_events
                ),
                "duplicate_events": (
                    self.duplicate_events
                ),
                "persistence_failures": (
                    self.persistence_failures
                ),
                "retry_attempts": (
                    self.retry_attempts
                ),
                "queue_full_drops": (
                    self.queue_full_drops
                ),
                (
                    "ignored_nonterminal_events"
                ): (
                    self
                    .ignored_nonterminal_events
                ),
                "ignored_untracked_events": (
                    self.ignored_untracked_events
                ),
                "worker_starts": (
                    self.worker_starts
                ),
            }
        )


class ProductionReliabilityAsyncWriter:
    """
    Persiste Reliability Events fora do caminho crítico.

    Garantias locais:
    - queue limitada;
    - enqueue não bloqueante;
    - worker lazy;
    - retry limitado;
    - falha do banco não propaga para Gemini/RAG;
    - flush explícito disponível;
    - nenhuma thread durante import.
    """

    def __init__(
        self,
        *,
        enabled: bool,
        max_queue_size: int = 1024,
        max_persist_attempts: int = 3,
        retry_base_delay_seconds: float = 0.25,
        persist_event: Callable[
            [ResilienceEvent],
            ProductionReliabilityLedgerWrite,
        ] = persist_production_reliability_event,
        initialize_schema: Callable[
            [],
            None,
        ] = initialize_production_reliability_schema,
        sleeper: Callable[
            [float],
            None,
        ] = time.sleep,
        clock: Callable[
            [],
            float,
        ] = time.monotonic,
    ) -> None:
        if (
            isinstance(
                max_queue_size,
                bool,
            )
            or max_queue_size < 1
        ):
            raise ValueError(
                "max_queue_size must be >= 1."
            )

        if (
            isinstance(
                max_persist_attempts,
                bool,
            )
            or max_persist_attempts < 1
        ):
            raise ValueError(
                "max_persist_attempts must be >= 1."
            )

        retry_base_delay_seconds = float(
            retry_base_delay_seconds
        )

        if (
            not math.isfinite(
                retry_base_delay_seconds
            )
            or retry_base_delay_seconds < 0
        ):
            raise ValueError(
                "retry_base_delay_seconds must "
                "be finite and >= 0."
            )

        self._enabled = bool(enabled)

        self._queue: queue.Queue[
            ResilienceEvent
        ] = queue.Queue(
            maxsize=max_queue_size
        )

        self._max_queue_size = (
            max_queue_size
        )

        self._max_persist_attempts = (
            max_persist_attempts
        )

        self._retry_base_delay_seconds = (
            retry_base_delay_seconds
        )

        self._persist_event = (
            persist_event
        )

        self._initialize_schema = (
            initialize_schema
        )

        self._sleeper = sleeper
        self._clock = clock

        self._state_lock = (
            threading.RLock()
        )

        self._flush_condition = (
            threading.Condition(
                self._state_lock
            )
        )

        self._worker_lock = (
            threading.Lock()
        )

        self._worker: (
            threading.Thread
            | None
        ) = None

        self._stop_event = (
            threading.Event()
        )

        self._schema_ready = False

        self._pending_events = 0
        self._enqueued_events = 0

        self._persisted_events = 0
        self._duplicate_events = 0

        self._persistence_failures = 0
        self._retry_attempts = 0
        self._queue_full_drops = 0

        self._ignored_nonterminal_events = 0
        self._ignored_untracked_events = 0

        self._worker_starts = 0

    @property
    def enabled(
        self,
    ) -> bool:
        return self._enabled

    def _ensure_worker_started(
        self,
    ) -> None:
        if not self._enabled:
            return

        with self._worker_lock:
            worker = self._worker

            if (
                worker is not None
                and worker.is_alive()
            ):
                return

            if self._stop_event.is_set():
                return

            worker = threading.Thread(
                target=self._run,
                name=(
                    "inna-production-"
                    "reliability-writer"
                ),
                daemon=True,
            )

            self._worker = worker

            with self._state_lock:
                self._worker_starts += 1

            worker.start()

    def enqueue(
        self,
        event: ResilienceEvent,
    ) -> bool:
        """
        Enfileira sem bloquear o caminho funcional.
        """
        if not self._enabled:
            return False

        if (
            event.operation
            not in PRODUCTION_RELIABILITY_POLICIES
        ):
            with self._state_lock:
                self._ignored_untracked_events += 1

            return False

        if (
            event.event_type
            not in _TERMINAL_EVENT_TYPES
        ):
            with self._state_lock:
                self._ignored_nonterminal_events += 1

            return False

        with self._flush_condition:
            if self._stop_event.is_set():
                return False

            try:
                self._queue.put_nowait(
                    event
                )

            except queue.Full:
                self._queue_full_drops += 1
                return False

            self._pending_events += 1
            self._enqueued_events += 1

            # O worker só pode consumir o evento depois
            # que o contador pending já estiver consistente.
            #
            # _state_lock é RLock, portanto a chamada é
            # segura mesmo dentro de _flush_condition.
            self._ensure_worker_started()

        return True

    def _ensure_schema(
        self,
    ) -> None:
        if self._schema_ready:
            return

        self._initialize_schema()

        self._schema_ready = True

    def _retry_delay(
        self,
        attempt_number: int,
    ) -> float:
        exponent = max(
            attempt_number - 1,
            0,
        )

        return min(
            self._retry_base_delay_seconds
            * (2**exponent),
            5.0,
        )

    def _persist_with_retry(
        self,
        event: ResilienceEvent,
    ) -> None:
        last_failure = False

        for attempt_number in range(
            1,
            self._max_persist_attempts + 1,
        ):
            try:
                self._ensure_schema()

                result = self._persist_event(
                    event
                )

                with self._state_lock:
                    if result.inserted:
                        self._persisted_events += 1
                    else:
                        self._duplicate_events += 1

                return

            except Exception:
                last_failure = True

                if (
                    attempt_number
                    >= self._max_persist_attempts
                ):
                    break

                with self._state_lock:
                    self._retry_attempts += 1

                delay = self._retry_delay(
                    attempt_number
                )

                if delay > 0:
                    self._sleeper(
                        delay
                    )

        if last_failure:
            with self._state_lock:
                self._persistence_failures += 1

    def _finish_pending_event(
        self,
    ) -> None:
        with self._flush_condition:
            self._pending_events = max(
                0,
                self._pending_events - 1,
            )

            if self._pending_events == 0:
                self._flush_condition.notify_all()

    def _run(
        self,
    ) -> None:
        while True:
            if (
                self._stop_event.is_set()
                and self._queue.empty()
            ):
                return

            try:
                event = self._queue.get(
                    timeout=0.10
                )

            except queue.Empty:
                continue

            try:
                self._persist_with_retry(
                    event
                )

            finally:
                self._queue.task_done()
                self._finish_pending_event()

    def flush(
        self,
        *,
        timeout_seconds: float = 5.0,
    ) -> bool:
        timeout_seconds = float(
            timeout_seconds
        )

        if (
            not math.isfinite(
                timeout_seconds
            )
            or timeout_seconds < 0
        ):
            raise ValueError(
                "timeout_seconds must be finite "
                "and >= 0."
            )

        if not self._enabled:
            return True

        deadline = (
            self._clock()
            + timeout_seconds
        )

        with self._flush_condition:
            while self._pending_events > 0:
                remaining = (
                    deadline
                    - self._clock()
                )

                if remaining <= 0:
                    return False

                self._flush_condition.wait(
                    timeout=remaining
                )

        return True

    def shutdown(
        self,
        *,
        timeout_seconds: float = 5.0,
    ) -> bool:
        if not self._enabled:
            return True

        timeout_seconds = float(
            timeout_seconds
        )

        if (
            not math.isfinite(
                timeout_seconds
            )
            or timeout_seconds < 0
        ):
            raise ValueError(
                "timeout_seconds must be finite "
                "and >= 0."
            )

        # Impede novos eventos antes do flush.
        # O worker continuará drenando tudo que já
        # foi aceito na queue.
        with self._flush_condition:
            self._stop_event.set()

        flushed = self.flush(
            timeout_seconds=(
                timeout_seconds
            )
        )

        worker = self._worker

        if (
            worker is not None
            and worker.is_alive()
        ):
            worker.join(
                timeout=timeout_seconds
            )

        worker_stopped = (
            worker is None
            or not worker.is_alive()
        )

        return (
            flushed
            and worker_stopped
        )

    def snapshot(
        self,
    ) -> ProductionReliabilityWriterSnapshot:
        with self._state_lock:
            worker = self._worker

            return (
                ProductionReliabilityWriterSnapshot(
                    enabled=self._enabled,
                    worker_running=(
                        worker is not None
                        and worker.is_alive()
                    ),
                    queue_capacity=(
                        self._max_queue_size
                    ),
                    pending_events=(
                        self._pending_events
                    ),
                    enqueued_events=(
                        self._enqueued_events
                    ),
                    persisted_events=(
                        self._persisted_events
                    ),
                    duplicate_events=(
                        self._duplicate_events
                    ),
                    persistence_failures=(
                        self._persistence_failures
                    ),
                    retry_attempts=(
                        self._retry_attempts
                    ),
                    queue_full_drops=(
                        self._queue_full_drops
                    ),
                    ignored_nonterminal_events=(
                        self
                        ._ignored_nonterminal_events
                    ),
                    ignored_untracked_events=(
                        self
                        ._ignored_untracked_events
                    ),
                    worker_starts=(
                        self._worker_starts
                    ),
                )
            )


_SINGLETON_LOCK = threading.Lock()

_PRODUCTION_RELIABILITY_WRITER: (
    ProductionReliabilityAsyncWriter
    | None
) = None


def _build_writer_from_environment(
) -> ProductionReliabilityAsyncWriter:
    return ProductionReliabilityAsyncWriter(
        enabled=_env_bool(
            (
                "INNA_RELIABILITY_"
                "LEDGER_ENABLED"
            ),
            default=False,
        ),
        max_queue_size=_env_positive_int(
            (
                "INNA_RELIABILITY_"
                "LEDGER_QUEUE_SIZE"
            ),
            default=1024,
        ),
        max_persist_attempts=(
            _env_positive_int(
                (
                    "INNA_RELIABILITY_"
                    "LEDGER_MAX_PERSIST_ATTEMPTS"
                ),
                default=3,
            )
        ),
        retry_base_delay_seconds=(
            _env_nonnegative_float(
                (
                    "INNA_RELIABILITY_"
                    "LEDGER_RETRY_BASE_DELAY_SECONDS"
                ),
                default=0.25,
            )
        ),
    )


def get_production_reliability_writer(
) -> ProductionReliabilityAsyncWriter:
    global _PRODUCTION_RELIABILITY_WRITER

    current = (
        _PRODUCTION_RELIABILITY_WRITER
    )

    if current is not None:
        return current

    with _SINGLETON_LOCK:
        current = (
            _PRODUCTION_RELIABILITY_WRITER
        )

        if current is None:
            current = (
                _build_writer_from_environment()
            )

            _PRODUCTION_RELIABILITY_WRITER = (
                current
            )

        return current


def observe_production_reliability_persistence_event(
    event: ResilienceEvent,
) -> bool:
    """
    Adapter seguro usado pelo observer de produção.
    """
    return (
        get_production_reliability_writer()
        .enqueue(event)
    )


__all__ = [
    "ProductionReliabilityAsyncWriter",
    "ProductionReliabilityWriterSnapshot",
    "get_production_reliability_writer",
    "observe_production_reliability_persistence_event",
]
