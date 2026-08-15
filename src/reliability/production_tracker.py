"""Reliability operacional dos serviços reais da INNA."""

from __future__ import annotations

import math
import threading
import time
from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from src.resilience.events import (
    ResilienceEvent,
    ResilienceEventType,
)


class OperationalReliabilityState(StrEnum):
    """
    Saúde operacional da dependência no processo atual.

    Não representa ainda o Error Budget distribuído
    de longo prazo entre múltiplas réplicas.
    """

    INSUFFICIENT_DATA = "insufficient_data"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"


class OperationalBurnSeverity(StrEnum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


def _threshold_reached(
    value: float,
    threshold: float,
) -> bool:
    """
    Compara thresholds tolerando apenas ruído
    numérico de ponto flutuante.

    Um valor materialmente abaixo do threshold
    continua abaixo dele.
    """
    value = float(value)
    threshold = float(threshold)

    return (
        value > threshold
        or math.isclose(
            value,
            threshold,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
    )


@dataclass(frozen=True, slots=True)
class ProductionReliabilityPolicy:
    """
    Threshold operacional para um serviço real da INNA.

    window_seconds é deliberadamente uma janela curta
    operacional. O SLO persistente de longo prazo será
    uma camada separada.
    """

    operation: str
    objective_ratio: float = 0.995
    window_seconds: float = 900.0
    minimum_operations: int = 20
    warning_burn_rate: float = 2.0
    critical_burn_rate: float = 6.0

    def __post_init__(self) -> None:
        operation = str(
            self.operation
        ).strip()

        if not operation:
            raise ValueError(
                "operation cannot be empty."
            )

        objective = float(
            self.objective_ratio
        )

        if (
            not math.isfinite(objective)
            or objective <= 0.0
            or objective >= 1.0
        ):
            raise ValueError(
                "objective_ratio must be "
                "between 0 and 1."
            )

        window = float(
            self.window_seconds
        )

        if (
            not math.isfinite(window)
            or window <= 0.0
        ):
            raise ValueError(
                "window_seconds must be positive."
            )

        if (
            isinstance(
                self.minimum_operations,
                bool,
            )
            or not isinstance(
                self.minimum_operations,
                int,
            )
            or self.minimum_operations < 1
        ):
            raise ValueError(
                "minimum_operations must be "
                "an integer >= 1."
            )

        warning = float(
            self.warning_burn_rate
        )

        critical = float(
            self.critical_burn_rate
        )

        if (
            not math.isfinite(warning)
            or warning < 1.0
        ):
            raise ValueError(
                "warning_burn_rate must be >= 1."
            )

        if (
            not math.isfinite(critical)
            or critical <= warning
        ):
            raise ValueError(
                "critical_burn_rate must exceed "
                "warning_burn_rate."
            )

        object.__setattr__(
            self,
            "operation",
            operation,
        )

        object.__setattr__(
            self,
            "objective_ratio",
            objective,
        )

        object.__setattr__(
            self,
            "window_seconds",
            window,
        )

        object.__setattr__(
            self,
            "warning_burn_rate",
            warning,
        )

        object.__setattr__(
            self,
            "critical_burn_rate",
            critical,
        )

    @property
    def error_budget_ratio(self) -> float:
        return 1.0 - self.objective_ratio


# Targets operacionais iniciais.
#
# 99,5%, burn warning 2x e critical 6x mantêm
# a mesma semântica matemática já validada no
# SLO operacional do Telegram.
#
# Estes valores são health thresholds do processo,
# não um compromisso de SLA comercial.
PRODUCTION_RELIABILITY_POLICIES = MappingProxyType(
    {
        "gemini.embedding": ProductionReliabilityPolicy(
            operation="gemini.embedding",
        ),
        (
            "gemini.generate.supervisor"
        ): ProductionReliabilityPolicy(
            operation=(
                "gemini.generate.supervisor"
            ),
        ),
        (
            "gemini.generate.text_service"
        ): ProductionReliabilityPolicy(
            operation=(
                "gemini.generate.text_service"
            ),
        ),
        "rag.agentic.planner": ProductionReliabilityPolicy(
            operation="rag.agentic.planner",
        ),
    }
)


@dataclass(frozen=True, slots=True)
class _LogicalOutcome:
    timestamp: float
    succeeded: bool
    circuit_rejected: bool


@dataclass(frozen=True, slots=True)
class ProductionReliabilitySnapshot:
    operation: str
    state: OperationalReliabilityState
    burn_severity: OperationalBurnSeverity | None

    objective_ratio: float
    error_budget_ratio: float
    window_seconds: float
    minimum_operations: int

    total_operations: int
    successful_operations: int
    failed_operations: int
    circuit_rejections: int

    observed_failure_ratio: float | None
    burn_rate: float | None

    @property
    def sample_sufficient(self) -> bool:
        return (
            self.total_operations
            >= self.minimum_operations
        )

    def to_safe_dict(
        self,
    ) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "operation": self.operation,
                "state": self.state.value,
                "burn_severity": (
                    self.burn_severity.value
                    if self.burn_severity
                    is not None
                    else None
                ),
                "objective_ratio": (
                    self.objective_ratio
                ),
                "error_budget_ratio": (
                    self.error_budget_ratio
                ),
                "window_seconds": (
                    self.window_seconds
                ),
                "minimum_operations": (
                    self.minimum_operations
                ),
                "total_operations": (
                    self.total_operations
                ),
                "successful_operations": (
                    self.successful_operations
                ),
                "failed_operations": (
                    self.failed_operations
                ),
                "circuit_rejections": (
                    self.circuit_rejections
                ),
                "observed_failure_ratio": (
                    self.observed_failure_ratio
                ),
                "burn_rate": self.burn_rate,
                "sample_sufficient": (
                    self.sample_sufficient
                ),
            }
        )


class ProductionReliabilityTracker:
    """
    Tracker process-local dos quatro serviços reais.

    Conta operações lógicas terminadas, não attempts.
    """

    def __init__(
        self,
        *,
        clock: Callable[[], float] = time.monotonic,
        policies: Mapping[
            str,
            ProductionReliabilityPolicy,
        ] = PRODUCTION_RELIABILITY_POLICIES,
    ) -> None:
        self._clock = clock
        self._policies = dict(
            policies
        )

        self._events: dict[
            str,
            deque[_LogicalOutcome],
        ] = {
            operation: deque()
            for operation in self._policies
        }

        self._lock = threading.RLock()

    @property
    def tracked_operations(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                self._policies
            )
        )

    def _expire(
        self,
        *,
        operation: str,
        now: float,
    ) -> None:
        policy = self._policies[
            operation
        ]

        queue = self._events[
            operation
        ]

        cutoff = (
            now
            - policy.window_seconds
        )

        while (
            queue
            and queue[0].timestamp < cutoff
        ):
            queue.popleft()

    def record_event(
        self,
        event: ResilienceEvent,
    ) -> bool:
        """
        Registra apenas o resultado lógico final.

        Retorna False quando o evento é de retry,
        attempt ou de uma operação não monitorada.
        """
        if (
            event.operation
            not in self._policies
        ):
            return False

        if (
            event.event_type
            is ResilienceEventType
            .OPERATION_SUCCEEDED
        ):
            succeeded = True
            circuit_rejected = False

        elif (
            event.event_type
            is ResilienceEventType
            .OPERATION_FAILED
        ):
            succeeded = False
            circuit_rejected = False

        elif (
            event.event_type
            is ResilienceEventType
            .CIRCUIT_REJECTED
        ):
            succeeded = False
            circuit_rejected = True

        else:
            return False

        now = float(
            self._clock()
        )

        if not math.isfinite(now):
            raise ValueError(
                "Reliability clock must be finite."
            )

        with self._lock:
            self._events[
                event.operation
            ].append(
                _LogicalOutcome(
                    timestamp=now,
                    succeeded=succeeded,
                    circuit_rejected=(
                        circuit_rejected
                    ),
                )
            )

            self._expire(
                operation=event.operation,
                now=now,
            )

        return True

    def snapshot(
        self,
        operation: str,
    ) -> ProductionReliabilitySnapshot:
        if operation not in self._policies:
            raise KeyError(
                f"Untracked operation: {operation}"
            )

        now = float(
            self._clock()
        )

        with self._lock:
            self._expire(
                operation=operation,
                now=now,
            )

            events = tuple(
                self._events[
                    operation
                ]
            )

        policy = self._policies[
            operation
        ]

        total = len(events)

        successes = sum(
            1
            for item in events
            if item.succeeded
        )

        failures = (
            total
            - successes
        )

        circuit_rejections = sum(
            1
            for item in events
            if item.circuit_rejected
        )

        if total == 0:
            observed_failure_ratio = None
            burn_rate = None
            burn_severity = None

        else:
            observed_failure_ratio = (
                failures
                / total
            )

            burn_rate = (
                observed_failure_ratio
                / policy.error_budget_ratio
            )

            if (
                _threshold_reached(
                    burn_rate,
                    policy.critical_burn_rate,
                )
            ):
                burn_severity = (
                    OperationalBurnSeverity
                    .CRITICAL
                )

            elif (
                _threshold_reached(
                    burn_rate,
                    policy.warning_burn_rate,
                )
            ):
                burn_severity = (
                    OperationalBurnSeverity
                    .WARNING
                )

            else:
                burn_severity = (
                    OperationalBurnSeverity
                    .NORMAL
                )

        if (
            total
            < policy.minimum_operations
        ):
            state = (
                OperationalReliabilityState
                .INSUFFICIENT_DATA
            )

        elif (
            burn_rate is not None
            and _threshold_reached(
                burn_rate,
                policy.critical_burn_rate,
            )
        ):
            state = (
                OperationalReliabilityState
                .CRITICAL
            )

        elif (
            burn_rate is not None
            and _threshold_reached(
                burn_rate,
                1.0,
            )
        ):
            state = (
                OperationalReliabilityState
                .DEGRADED
            )

        else:
            state = (
                OperationalReliabilityState
                .HEALTHY
            )

        return ProductionReliabilitySnapshot(
            operation=operation,
            state=state,
            burn_severity=burn_severity,
            objective_ratio=(
                policy.objective_ratio
            ),
            error_budget_ratio=(
                policy.error_budget_ratio
            ),
            window_seconds=(
                policy.window_seconds
            ),
            minimum_operations=(
                policy.minimum_operations
            ),
            total_operations=total,
            successful_operations=successes,
            failed_operations=failures,
            circuit_rejections=(
                circuit_rejections
            ),
            observed_failure_ratio=(
                observed_failure_ratio
            ),
            burn_rate=burn_rate,
        )

    def snapshot_all(
        self,
    ) -> Mapping[
        str,
        ProductionReliabilitySnapshot,
    ]:
        return MappingProxyType(
            {
                operation: (
                    self.snapshot(
                        operation
                    )
                )
                for operation
                in self.tracked_operations
            }
        )

    def clear(
        self,
        operation: str | None = None,
    ) -> None:
        with self._lock:
            if operation is None:
                for queue in (
                    self._events.values()
                ):
                    queue.clear()

                return

            if (
                operation
                not in self._events
            ):
                raise KeyError(
                    f"Untracked operation: "
                    f"{operation}"
                )

            self._events[
                operation
            ].clear()


_PRODUCTION_RELIABILITY_TRACKER = (
    ProductionReliabilityTracker()
)


def get_production_reliability_tracker(
) -> ProductionReliabilityTracker:
    return _PRODUCTION_RELIABILITY_TRACKER


def observe_production_reliability_event(
    event: ResilienceEvent,
) -> bool:
    return (
        _PRODUCTION_RELIABILITY_TRACKER
        .record_event(event)
    )


__all__ = [
    "OperationalBurnSeverity",
    "OperationalReliabilityState",
    "PRODUCTION_RELIABILITY_POLICIES",
    "ProductionReliabilityPolicy",
    "ProductionReliabilitySnapshot",
    "ProductionReliabilityTracker",
    "get_production_reliability_tracker",
    "observe_production_reliability_event",
]
