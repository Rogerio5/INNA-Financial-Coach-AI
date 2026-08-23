from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass, replace
from typing import Callable

from .health_readiness import (
    TelegramOperationalSnapshot,
    TelegramOperationalStatus,
    TelegramOperationalStatusService,
    TelegramProbeResult,
    TelegramProbeSeverity,
    TelegramProbeStatus,
)


def _validate_non_negative_finite(
    name: str,
    value: object,
) -> float:
    try:
        normalized = float(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            f"{name} deve ser numérico."
        ) from exc

    if (
        math.isnan(normalized)
        or math.isinf(normalized)
        or normalized < 0
    ):
        raise ValueError(
            f"{name} deve ser finito e não negativo."
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramReadinessRuntimePolicy:
    cache_ttl_seconds: float = 1.0
    concurrent_wait_seconds: float = 0.25
    evaluation_budget_seconds: float = 2.0

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "cache_ttl_seconds",
            _validate_non_negative_finite(
                "cache_ttl_seconds",
                self.cache_ttl_seconds,
            ),
        )

        object.__setattr__(
            self,
            "concurrent_wait_seconds",
            _validate_non_negative_finite(
                "concurrent_wait_seconds",
                self.concurrent_wait_seconds,
            ),
        )

        object.__setattr__(
            self,
            "evaluation_budget_seconds",
            _validate_non_negative_finite(
                "evaluation_budget_seconds",
                self.evaluation_budget_seconds,
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramReadinessRuntimeResult:
    snapshot: TelegramOperationalSnapshot
    sequence: int
    cache_hit: bool
    cache_age_seconds: float
    generated_at_epoch_seconds: float
    reason: str

    @property
    def ready(
        self,
    ) -> bool:
        return self.snapshot.ready

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "cache_hit": self.cache_hit,
            "cache_age_seconds": (
                self.cache_age_seconds
            ),
            "generated_at_epoch_seconds": (
                self.generated_at_epoch_seconds
            ),
            "reason": self.reason,
            "operational": (
                self.snapshot.to_safe_dict()
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class _CachedReadiness:
    result: TelegramReadinessRuntimeResult
    created_monotonic: float


class TelegramReadinessRuntime:
    def __init__(
        self,
        service: TelegramOperationalStatusService,
        *,
        policy: (
            TelegramReadinessRuntimePolicy
            | None
        ) = None,
        monotonic_clock: Callable[
            [],
            float
        ] = time.monotonic,
        wall_clock: Callable[
            [],
            float
        ] = time.time,
    ) -> None:
        self._service = service

        self._policy = (
            policy
            or TelegramReadinessRuntimePolicy()
        )

        self._monotonic_clock = (
            monotonic_clock
        )

        self._wall_clock = wall_clock

        self._condition = (
            threading.Condition(
                threading.RLock()
            )
        )

        self._refreshing = False
        self._cache: _CachedReadiness | None = None
        self._sequence = 0

    @property
    def policy(
        self,
    ) -> TelegramReadinessRuntimePolicy:
        return self._policy

    def invalidate(
        self,
    ) -> None:
        with self._condition:
            self._cache = None

    def evaluate(
        self,
        *,
        force_refresh: bool = False,
    ) -> TelegramReadinessRuntimeResult:
        now = self._monotonic_clock()

        with self._condition:
            cached = self._fresh_cached_result(
                now=now,
                force_refresh=force_refresh,
            )

            if cached is not None:
                return cached

            if self._refreshing:
                notified = self._condition.wait(
                    timeout=(
                        self._policy
                        .concurrent_wait_seconds
                    )
                )

                now = self._monotonic_clock()

                cached = self._fresh_cached_result(
                    now=now,
                    force_refresh=False,
                )

                if cached is not None:
                    return replace(
                        cached,
                        reason=(
                            "single_flight_cache"
                        ),
                    )

                if not notified:
                    return (
                        self._build_runtime_failure(
                            reason=(
                                "concurrent_wait_timeout"
                            ),
                            error_category="timeout",
                            details={
                                "refresh_in_progress": True,
                            },
                        )
                    )

                if self._refreshing:
                    return (
                        self._build_runtime_failure(
                            reason=(
                                "refresh_still_in_progress"
                            ),
                            error_category="timeout",
                            details={
                                "refresh_in_progress": True,
                            },
                        )
                    )

            self._refreshing = True

        started_at = (
            self._monotonic_clock()
        )

        try:
            snapshot = (
                self._service.evaluate()
            )

            elapsed = max(
                0.0,
                self._monotonic_clock()
                - started_at,
            )

            if (
                elapsed
                > self._policy
                .evaluation_budget_seconds
            ):
                snapshot = (
                    self._apply_budget_failure(
                        snapshot=snapshot,
                        elapsed=elapsed,
                    )
                )

                reason = (
                    "evaluation_budget_exceeded"
                )

            else:
                reason = "evaluated"

            result = self._build_result(
                snapshot=snapshot,
                reason=reason,
            )

        except Exception:
            result = (
                self._build_runtime_failure(
                    reason="evaluation_exception",
                    error_category="internal",
                    details={
                        "exception": True,
                    },
                )
            )

        with self._condition:
            self._cache = _CachedReadiness(
                result=result,
                created_monotonic=(
                    self._monotonic_clock()
                ),
            )

            self._refreshing = False
            self._condition.notify_all()

        return result

    def _fresh_cached_result(
        self,
        *,
        now: float,
        force_refresh: bool,
    ) -> TelegramReadinessRuntimeResult | None:
        if (
            force_refresh
            or self._cache is None
        ):
            return None

        age = max(
            0.0,
            now
            - self._cache.created_monotonic,
        )

        if (
            age
            > self._policy
            .cache_ttl_seconds
        ):
            return None

        return replace(
            self._cache.result,
            cache_hit=True,
            cache_age_seconds=age,
            reason="cache",
        )

    def _build_result(
        self,
        *,
        snapshot: TelegramOperationalSnapshot,
        reason: str,
    ) -> TelegramReadinessRuntimeResult:
        self._sequence += 1

        return TelegramReadinessRuntimeResult(
            snapshot=snapshot,
            sequence=self._sequence,
            cache_hit=False,
            cache_age_seconds=0.0,
            generated_at_epoch_seconds=(
                self._wall_clock()
            ),
            reason=reason,
        )

    def _build_runtime_failure(
        self,
        *,
        reason: str,
        error_category: str,
        details: dict[str, object],
    ) -> TelegramReadinessRuntimeResult:
        probe = TelegramProbeResult(
            name="readiness_runtime",
            status=TelegramProbeStatus.FAIL,
            severity=(
                TelegramProbeSeverity.REQUIRED
            ),
            latency_seconds=0.0,
            error_category=error_category,
            details=details,
        )

        snapshot = TelegramOperationalSnapshot(
            status=(
                TelegramOperationalStatus.UNREADY
            ),
            checks=(probe,),
            checked_at_epoch_seconds=(
                self._wall_clock()
            ),
            total_latency_seconds=0.0,
        )

        return self._build_result(
            snapshot=snapshot,
            reason=reason,
        )

    def _apply_budget_failure(
        self,
        *,
        snapshot: TelegramOperationalSnapshot,
        elapsed: float,
    ) -> TelegramOperationalSnapshot:
        budget_check = TelegramProbeResult(
            name="readiness_runtime_budget",
            status=TelegramProbeStatus.FAIL,
            severity=(
                TelegramProbeSeverity.REQUIRED
            ),
            latency_seconds=elapsed,
            error_category="timeout",
            details={
                "budget_exceeded": True,
            },
        )

        return TelegramOperationalSnapshot(
            status=(
                TelegramOperationalStatus.UNREADY
            ),
            checks=(
                snapshot.checks
                + (
                    budget_check,
                )
            ),
            checked_at_epoch_seconds=(
                snapshot
                .checked_at_epoch_seconds
            ),
            total_latency_seconds=max(
                snapshot.total_latency_seconds,
                elapsed,
            ),
        )


__all__ = [
    "TelegramReadinessRuntime",
    "TelegramReadinessRuntimePolicy",
    "TelegramReadinessRuntimeResult",
]
