from __future__ import annotations

import math
import time
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Callable, Mapping, Protocol


class TelegramOperationalStatus(
    str,
    Enum,
):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNREADY = "unready"


class TelegramProbeStatus(
    str,
    Enum,
):
    PASS = "pass"
    FAIL = "fail"


class TelegramProbeSeverity(
    str,
    Enum,
):
    REQUIRED = "required"
    OPTIONAL = "optional"
    INFORMATIONAL = "informational"


_ALLOWED_ERROR_CATEGORIES = frozenset(
    {
        "none",
        "configuration",
        "dependency",
        "database",
        "persistence",
        "encryption",
        "timeout",
        "consistency",
        "internal",
        "unknown",
    }
)


def _normalize_error_category(
    value: object,
) -> str:
    normalized = str(
        value
        or "unknown"
    ).strip().lower()

    if normalized in (
        _ALLOWED_ERROR_CATEGORIES
    ):
        return normalized

    return "unknown"


def _normalize_latency(
    value: object,
) -> float:
    try:
        latency = float(
            value
        )
    except (
        TypeError,
        ValueError,
    ):
        return 0.0

    if (
        math.isnan(latency)
        or math.isinf(latency)
        or latency < 0
    ):
        return 0.0

    return latency


def _safe_details(
    details: (
        Mapping[str, object]
        | None
    ),
) -> Mapping[str, object]:
    if not details:
        return MappingProxyType(
            {}
        )

    normalized: dict[
        str,
        object
    ] = {}

    for raw_name, raw_value in (
        details.items()
    ):
        name = str(
            raw_name
        ).strip()

        if not name:
            continue

        if isinstance(
            raw_value,
            (
                bool,
                int,
                float,
                type(None),
            ),
        ):
            normalized[
                name
            ] = raw_value

        elif isinstance(
            raw_value,
            Enum,
        ):
            normalized[
                name
            ] = raw_value.value

        else:
            normalized[
                name
            ] = str(
                raw_value
            )[:120]

    return MappingProxyType(
        normalized
    )


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramProbeResult:
    name: str
    status: TelegramProbeStatus
    severity: TelegramProbeSeverity
    latency_seconds: float
    error_category: str
    details: Mapping[str, object]

    def __post_init__(
        self,
    ) -> None:
        normalized_name = str(
            self.name
        ).strip()

        if not normalized_name:
            raise ValueError(
                "Probe sem nome."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )

        object.__setattr__(
            self,
            "status",
            TelegramProbeStatus(
                self.status
            ),
        )

        object.__setattr__(
            self,
            "severity",
            TelegramProbeSeverity(
                self.severity
            ),
        )

        object.__setattr__(
            self,
            "latency_seconds",
            _normalize_latency(
                self.latency_seconds
            ),
        )

        object.__setattr__(
            self,
            "error_category",
            _normalize_error_category(
                self.error_category
            ),
        )

        object.__setattr__(
            self,
            "details",
            _safe_details(
                self.details
            ),
        )

    @property
    def passed(
        self,
    ) -> bool:
        return (
            self.status
            is TelegramProbeStatus.PASS
        )

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "name": self.name,
            "status": self.status.value,
            "severity": self.severity.value,
            "latency_seconds": (
                self.latency_seconds
            ),
            "error_category": (
                self.error_category
            ),
            "details": dict(
                self.details
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramOperationalSnapshot:
    status: TelegramOperationalStatus
    checks: tuple[
        TelegramProbeResult,
        ...,
    ]
    checked_at_epoch_seconds: float
    total_latency_seconds: float

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "status",
            TelegramOperationalStatus(
                self.status
            ),
        )

        object.__setattr__(
            self,
            "checks",
            tuple(
                self.checks
            ),
        )

        object.__setattr__(
            self,
            "checked_at_epoch_seconds",
            float(
                self.checked_at_epoch_seconds
            ),
        )

        object.__setattr__(
            self,
            "total_latency_seconds",
            _normalize_latency(
                self.total_latency_seconds
            ),
        )

    @property
    def ready(
        self,
    ) -> bool:
        return (
            self.status
            is not TelegramOperationalStatus
            .UNREADY
        )

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "status": self.status.value,
            "ready": self.ready,
            "checked_at_epoch_seconds": (
                self.checked_at_epoch_seconds
            ),
            "total_latency_seconds": (
                self.total_latency_seconds
            ),
            "checks": [
                check.to_safe_dict()
                for check in self.checks
            ],
        }


class TelegramProbe(
    Protocol,
):
    @property
    def name(
        self,
    ) -> str:
        ...

    @property
    def severity(
        self,
    ) -> TelegramProbeSeverity:
        ...

    def run(
        self,
    ) -> TelegramProbeResult:
        ...


ProbeCallable = Callable[
    [],
    (
        bool
        | Mapping[str, object]
        | TelegramProbeResult
    ),
]


class CallableTelegramProbe:
    def __init__(
        self,
        *,
        name: str,
        severity: (
            TelegramProbeSeverity
            | str
        ),
        check: ProbeCallable,
        error_category: str = (
            "dependency"
        ),
        clock: Callable[
            [],
            float
        ] = time.perf_counter,
    ) -> None:
        normalized_name = str(
            name
        ).strip()

        if not normalized_name:
            raise ValueError(
                "Probe sem nome."
            )

        self._name = (
            normalized_name
        )

        self._severity = (
            TelegramProbeSeverity(
                severity
            )
        )

        self._check = check

        self._error_category = (
            _normalize_error_category(
                error_category
            )
        )

        self._clock = clock

    @property
    def name(
        self,
    ) -> str:
        return self._name

    @property
    def severity(
        self,
    ) -> TelegramProbeSeverity:
        return self._severity

    def run(
        self,
    ) -> TelegramProbeResult:
        started_at = (
            self._clock()
        )

        try:
            raw_result = (
                self._check()
            )

            latency = (
                self._clock()
                - started_at
            )

            if isinstance(
                raw_result,
                TelegramProbeResult,
            ):
                return (
                    TelegramProbeResult(
                        name=self._name,
                        status=(
                            raw_result.status
                        ),
                        severity=(
                            self._severity
                        ),
                        latency_seconds=(
                            latency
                        ),
                        error_category=(
                            raw_result
                            .error_category
                        ),
                        details=(
                            raw_result.details
                        ),
                    )
                )

            if isinstance(
                raw_result,
                Mapping,
            ):
                passed = bool(
                    raw_result.get(
                        "passed",
                        True,
                    )
                )

                details = {
                    key: value
                    for key, value
                    in raw_result.items()
                    if key != "passed"
                }

            else:
                passed = bool(
                    raw_result
                )

                details = {}

            return TelegramProbeResult(
                name=self._name,
                status=(
                    TelegramProbeStatus.PASS
                    if passed
                    else TelegramProbeStatus.FAIL
                ),
                severity=self._severity,
                latency_seconds=latency,
                error_category=(
                    "none"
                    if passed
                    else self._error_category
                ),
                details=details,
            )

        except Exception:
            latency = (
                self._clock()
                - started_at
            )

            return TelegramProbeResult(
                name=self._name,
                status=(
                    TelegramProbeStatus.FAIL
                ),
                severity=self._severity,
                latency_seconds=latency,
                error_category=(
                    self._error_category
                ),
                details={
                    "exception": True,
                },
            )


class TelegramOperationalStatusService:
    def __init__(
        self,
        probes: tuple[
            TelegramProbe,
            ...,
        ],
        *,
        wall_clock: Callable[
            [],
            float
        ] = time.time,
        monotonic_clock: Callable[
            [],
            float
        ] = time.perf_counter,
    ) -> None:
        self._probes = tuple(
            probes
        )

        self._wall_clock = (
            wall_clock
        )

        self._monotonic_clock = (
            monotonic_clock
        )

    def evaluate(
        self,
    ) -> TelegramOperationalSnapshot:
        started_at = (
            self._monotonic_clock()
        )

        results = tuple(
            probe.run()
            for probe in self._probes
        )

        status = (
            self._resolve_status(
                results
            )
        )

        return TelegramOperationalSnapshot(
            status=status,
            checks=results,
            checked_at_epoch_seconds=(
                self._wall_clock()
            ),
            total_latency_seconds=(
                self._monotonic_clock()
                - started_at
            ),
        )

    @staticmethod
    def _resolve_status(
        results: tuple[
            TelegramProbeResult,
            ...,
        ],
    ) -> TelegramOperationalStatus:
        has_required_failure = any(
            (
                not result.passed
                and result.severity
                is TelegramProbeSeverity
                .REQUIRED
            )
            for result in results
        )

        if has_required_failure:
            return (
                TelegramOperationalStatus
                .UNREADY
            )

        has_optional_failure = any(
            (
                not result.passed
                and result.severity
                is TelegramProbeSeverity
                .OPTIONAL
            )
            for result in results
        )

        if has_optional_failure:
            return (
                TelegramOperationalStatus
                .DEGRADED
            )

        return (
            TelegramOperationalStatus
            .HEALTHY
        )


def create_process_health_service(
    *,
    clock_check: Callable[
        [],
        bool
    ] = lambda: True,
) -> TelegramOperationalStatusService:
    return TelegramOperationalStatusService(
        probes=(
            CallableTelegramProbe(
                name="process",
                severity=(
                    TelegramProbeSeverity
                    .REQUIRED
                ),
                check=clock_check,
                error_category="internal",
            ),
        )
    )


__all__ = [
    "CallableTelegramProbe",
    "TelegramOperationalSnapshot",
    "TelegramOperationalStatus",
    "TelegramOperationalStatusService",
    "TelegramProbe",
    "TelegramProbeResult",
    "TelegramProbeSeverity",
    "TelegramProbeStatus",
    "create_process_health_service",
]
