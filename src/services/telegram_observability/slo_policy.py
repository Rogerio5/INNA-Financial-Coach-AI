from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class TelegramSloPolicyError(
    ValueError
):
    pass


class TelegramSloSeverity(
    str,
    Enum,
):
    WARNING = "warning"
    CRITICAL = "critical"


def _finite_float(
    *,
    name: str,
    value: object,
    minimum: float,
    maximum: float,
) -> float:
    try:
        normalized = float(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise TelegramSloPolicyError(
            f"{name} deve ser numérico."
        ) from exc

    if (
        math.isnan(normalized)
        or math.isinf(normalized)
    ):
        raise TelegramSloPolicyError(
            f"{name} deve ser finito."
        )

    if normalized < minimum:
        raise TelegramSloPolicyError(
            f"{name} deve ser maior ou igual a "
            f"{minimum}."
        )

    if normalized > maximum:
        raise TelegramSloPolicyError(
            f"{name} deve ser menor ou igual a "
            f"{maximum}."
        )

    return normalized


def _positive_integer(
    *,
    name: str,
    value: object,
    minimum: int = 1,
) -> int:
    if isinstance(
        value,
        bool,
    ):
        raise TelegramSloPolicyError(
            f"{name} deve ser inteiro."
        )

    try:
        normalized = int(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise TelegramSloPolicyError(
            f"{name} deve ser inteiro."
        ) from exc

    if normalized < minimum:
        raise TelegramSloPolicyError(
            f"{name} deve ser maior ou igual a "
            f"{minimum}."
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramAvailabilitySlo:
    objective_ratio: float = 0.995
    window_days: int = 30
    warning_burn_rate: float = 2.0
    critical_burn_rate: float = 6.0

    def __post_init__(
        self,
    ) -> None:
        objective = _finite_float(
            name="objective_ratio",
            value=self.objective_ratio,
            minimum=0.90,
            maximum=0.99999,
        )

        window_days = _positive_integer(
            name="window_days",
            value=self.window_days,
        )

        warning_burn_rate = _finite_float(
            name="warning_burn_rate",
            value=self.warning_burn_rate,
            minimum=1.0,
            maximum=100.0,
        )

        critical_burn_rate = _finite_float(
            name="critical_burn_rate",
            value=self.critical_burn_rate,
            minimum=1.0,
            maximum=1000.0,
        )

        if (
            critical_burn_rate
            <= warning_burn_rate
        ):
            raise TelegramSloPolicyError(
                "critical_burn_rate deve ser maior "
                "que warning_burn_rate."
            )

        object.__setattr__(
            self,
            "objective_ratio",
            objective,
        )

        object.__setattr__(
            self,
            "window_days",
            window_days,
        )

        object.__setattr__(
            self,
            "warning_burn_rate",
            warning_burn_rate,
        )

        object.__setattr__(
            self,
            "critical_burn_rate",
            critical_burn_rate,
        )

    @property
    def error_budget_ratio(
        self,
    ) -> float:
        return 1.0 - self.objective_ratio

    @property
    def window_seconds(
        self,
    ) -> int:
        return (
            self.window_days
            * 24
            * 60
            * 60
        )

    @property
    def allowed_unavailable_seconds(
        self,
    ) -> float:
        return (
            self.window_seconds
            * self.error_budget_ratio
        )


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramSuccessRateSlo:
    objective_ratio: float = 0.99

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "objective_ratio",
            _finite_float(
                name="objective_ratio",
                value=self.objective_ratio,
                minimum=0.90,
                maximum=0.99999,
            ),
        )

    @property
    def failure_budget_ratio(
        self,
    ) -> float:
        return 1.0 - self.objective_ratio


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramLatencySlo:
    p95_seconds: float = 2.0
    p99_seconds: float = 5.0

    def __post_init__(
        self,
    ) -> None:
        p95 = _finite_float(
            name="p95_seconds",
            value=self.p95_seconds,
            minimum=0.001,
            maximum=300.0,
        )

        p99 = _finite_float(
            name="p99_seconds",
            value=self.p99_seconds,
            minimum=0.001,
            maximum=600.0,
        )

        if p99 < p95:
            raise TelegramSloPolicyError(
                "p99_seconds deve ser maior ou "
                "igual a p95_seconds."
            )

        object.__setattr__(
            self,
            "p95_seconds",
            p95,
        )

        object.__setattr__(
            self,
            "p99_seconds",
            p99,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramBacklogSlo:
    warning_jobs: int = 25
    critical_jobs: int = 100

    def __post_init__(
        self,
    ) -> None:
        warning = _positive_integer(
            name="warning_jobs",
            value=self.warning_jobs,
            minimum=0,
        )

        critical = _positive_integer(
            name="critical_jobs",
            value=self.critical_jobs,
            minimum=1,
        )

        if critical <= warning:
            raise TelegramSloPolicyError(
                "critical_jobs deve ser maior que "
                "warning_jobs."
            )

        object.__setattr__(
            self,
            "warning_jobs",
            warning,
        )

        object.__setattr__(
            self,
            "critical_jobs",
            critical,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramDeadLetterSlo:
    warning_count: int = 1
    critical_count: int = 5

    def __post_init__(
        self,
    ) -> None:
        warning = _positive_integer(
            name="warning_count",
            value=self.warning_count,
            minimum=1,
        )

        critical = _positive_integer(
            name="critical_count",
            value=self.critical_count,
            minimum=1,
        )

        if critical <= warning:
            raise TelegramSloPolicyError(
                "critical_count deve ser maior que "
                "warning_count."
            )

        object.__setattr__(
            self,
            "warning_count",
            warning,
        )

        object.__setattr__(
            self,
            "critical_count",
            critical,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramMetricFreshnessSlo:
    warning_seconds: float = 120.0
    critical_seconds: float = 300.0

    def __post_init__(
        self,
    ) -> None:
        warning = _finite_float(
            name="warning_seconds",
            value=self.warning_seconds,
            minimum=1.0,
            maximum=86400.0,
        )

        critical = _finite_float(
            name="critical_seconds",
            value=self.critical_seconds,
            minimum=1.0,
            maximum=86400.0,
        )

        if critical <= warning:
            raise TelegramSloPolicyError(
                "critical_seconds deve ser maior "
                "que warning_seconds."
            )

        object.__setattr__(
            self,
            "warning_seconds",
            warning,
        )

        object.__setattr__(
            self,
            "critical_seconds",
            critical,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramSloWindows:
    short_window_seconds: int = 300
    medium_window_seconds: int = 3600
    long_window_seconds: int = 2592000

    def __post_init__(
        self,
    ) -> None:
        short = _positive_integer(
            name="short_window_seconds",
            value=self.short_window_seconds,
        )

        medium = _positive_integer(
            name="medium_window_seconds",
            value=self.medium_window_seconds,
        )

        long = _positive_integer(
            name="long_window_seconds",
            value=self.long_window_seconds,
        )

        if not (
            short
            < medium
            < long
        ):
            raise TelegramSloPolicyError(
                "As janelas devem obedecer "
                "short < medium < long."
            )

        object.__setattr__(
            self,
            "short_window_seconds",
            short,
        )

        object.__setattr__(
            self,
            "medium_window_seconds",
            medium,
        )

        object.__setattr__(
            self,
            "long_window_seconds",
            long,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramOperationalSloPolicy:
    availability: TelegramAvailabilitySlo = (
        TelegramAvailabilitySlo()
    )

    success_rate: TelegramSuccessRateSlo = (
        TelegramSuccessRateSlo()
    )

    latency: TelegramLatencySlo = (
        TelegramLatencySlo()
    )

    backlog: TelegramBacklogSlo = (
        TelegramBacklogSlo()
    )

    dead_letter: TelegramDeadLetterSlo = (
        TelegramDeadLetterSlo()
    )

    freshness: TelegramMetricFreshnessSlo = (
        TelegramMetricFreshnessSlo()
    )

    windows: TelegramSloWindows = (
        TelegramSloWindows()
    )

    def to_safe_dict(
        self,
    ) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "availability": {
                    "objective_ratio": (
                        self
                        .availability
                        .objective_ratio
                    ),
                    "error_budget_ratio": (
                        self
                        .availability
                        .error_budget_ratio
                    ),
                    "window_days": (
                        self
                        .availability
                        .window_days
                    ),
                    "allowed_unavailable_seconds": (
                        self
                        .availability
                        .allowed_unavailable_seconds
                    ),
                    "warning_burn_rate": (
                        self
                        .availability
                        .warning_burn_rate
                    ),
                    "critical_burn_rate": (
                        self
                        .availability
                        .critical_burn_rate
                    ),
                },
                "success_rate": {
                    "objective_ratio": (
                        self
                        .success_rate
                        .objective_ratio
                    ),
                    "failure_budget_ratio": (
                        self
                        .success_rate
                        .failure_budget_ratio
                    ),
                },
                "latency": {
                    "p95_seconds": (
                        self.latency.p95_seconds
                    ),
                    "p99_seconds": (
                        self.latency.p99_seconds
                    ),
                },
                "backlog": {
                    "warning_jobs": (
                        self.backlog.warning_jobs
                    ),
                    "critical_jobs": (
                        self.backlog.critical_jobs
                    ),
                },
                "dead_letter": {
                    "warning_count": (
                        self
                        .dead_letter
                        .warning_count
                    ),
                    "critical_count": (
                        self
                        .dead_letter
                        .critical_count
                    ),
                },
                "freshness": {
                    "warning_seconds": (
                        self
                        .freshness
                        .warning_seconds
                    ),
                    "critical_seconds": (
                        self
                        .freshness
                        .critical_seconds
                    ),
                },
                "windows": {
                    "short_window_seconds": (
                        self
                        .windows
                        .short_window_seconds
                    ),
                    "medium_window_seconds": (
                        self
                        .windows
                        .medium_window_seconds
                    ),
                    "long_window_seconds": (
                        self
                        .windows
                        .long_window_seconds
                    ),
                },
            }
        )


def classify_threshold(
    *,
    value: float,
    warning_threshold: float,
    critical_threshold: float,
) -> TelegramSloSeverity | None:
    normalized_value = _finite_float(
        name="value",
        value=value,
        minimum=0.0,
        maximum=float(
            10**15
        ),
    )

    warning = _finite_float(
        name="warning_threshold",
        value=warning_threshold,
        minimum=0.0,
        maximum=float(
            10**15
        ),
    )

    critical = _finite_float(
        name="critical_threshold",
        value=critical_threshold,
        minimum=0.0,
        maximum=float(
            10**15
        ),
    )

    if critical <= warning:
        raise TelegramSloPolicyError(
            "critical_threshold deve ser maior "
            "que warning_threshold."
        )

    critical_reached = (
        normalized_value >= critical
        or math.isclose(
            normalized_value,
            critical,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
    )

    warning_reached = (
        normalized_value >= warning
        or math.isclose(
            normalized_value,
            warning,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
    )

    if critical_reached:
        return TelegramSloSeverity.CRITICAL

    if warning_reached:
        return TelegramSloSeverity.WARNING

    return None


def calculate_burn_rate(
    *,
    observed_error_ratio: float,
    objective_ratio: float,
) -> float:
    observed_error = _finite_float(
        name="observed_error_ratio",
        value=observed_error_ratio,
        minimum=0.0,
        maximum=1.0,
    )

    objective = _finite_float(
        name="objective_ratio",
        value=objective_ratio,
        minimum=0.0,
        maximum=0.999999999,
    )

    error_budget = 1.0 - objective

    if error_budget <= 0:
        raise TelegramSloPolicyError(
            "O error budget deve ser maior que zero."
        )

    return observed_error / error_budget


def classify_burn_rate(
    *,
    burn_rate: float,
    availability: (
        TelegramAvailabilitySlo
        | None
    ) = None,
) -> TelegramSloSeverity | None:
    policy = (
        availability
        or TelegramAvailabilitySlo()
    )

    return classify_threshold(
        value=burn_rate,
        warning_threshold=(
            policy.warning_burn_rate
        ),
        critical_threshold=(
            policy.critical_burn_rate
        ),
    )


__all__ = [
    "TelegramAvailabilitySlo",
    "TelegramBacklogSlo",
    "TelegramDeadLetterSlo",
    "TelegramLatencySlo",
    "TelegramMetricFreshnessSlo",
    "TelegramOperationalSloPolicy",
    "TelegramSloPolicyError",
    "TelegramSloSeverity",
    "TelegramSloWindows",
    "TelegramSuccessRateSlo",
    "calculate_burn_rate",
    "classify_burn_rate",
    "classify_threshold",
]
