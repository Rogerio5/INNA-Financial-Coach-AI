from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from .contracts import FailureKind


class ResilienceEventType(StrEnum):
    ATTEMPT_STARTED = "attempt_started"
    ATTEMPT_FAILED = "attempt_failed"
    RETRY_SCHEDULED = "retry_scheduled"
    OPERATION_SUCCEEDED = "operation_succeeded"
    OPERATION_FAILED = "operation_failed"
    CIRCUIT_REJECTED = "circuit_rejected"


@dataclass(frozen=True, slots=True)
class ResilienceEvent:
    operation: str
    event_type: ResilienceEventType
    attempt_number: int
    max_attempts: int

    failure_kind: FailureKind | None = None
    error_type: str | None = None

    delay_seconds: float | None = None
    circuit_state: str | None = None
    elapsed_ms: float | None = None


ResilienceObserver = Callable[
    [ResilienceEvent],
    None,
]
