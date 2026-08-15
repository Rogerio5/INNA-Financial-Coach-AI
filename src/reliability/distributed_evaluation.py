"""Avaliação distribuída de Reliability da INNA."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from .production_tracker import (
    PRODUCTION_RELIABILITY_POLICIES,
    OperationalBurnSeverity,
    OperationalReliabilityState,
    ProductionReliabilitySnapshot,
    evaluate_production_reliability_counts,
)
from .shared_provider import (
    ReliabilityDataSource,
    SharedReliabilityProvider,
    SharedReliabilitySnapshot,
    get_shared_reliability_provider,
)


@dataclass(
    frozen=True,
    slots=True,
)
class DistributedReliabilitySnapshot:
    """
    Visão operacional efetiva da Reliability.

    A avaliação pode vir:
    - da janela compartilhada PostgreSQL/Neon;
    - do tracker local em fallback.

    Esta classe não executa I/O.
    """

    operation: str
    source: ReliabilityDataSource

    evaluation: ProductionReliabilitySnapshot

    shared_data_used: bool
    provider_enabled: bool

    cache_age_seconds: float | None
    cache_stale: bool

    database_unavailable: bool
    refresh_in_flight: bool

    @property
    def state(
        self,
    ) -> OperationalReliabilityState:
        return self.evaluation.state

    @property
    def burn_severity(
        self,
    ) -> OperationalBurnSeverity | None:
        return self.evaluation.burn_severity

    @property
    def burn_rate(
        self,
    ) -> float | None:
        return self.evaluation.burn_rate

    @property
    def sample_sufficient(
        self,
    ) -> bool:
        return self.evaluation.sample_sufficient

    def to_safe_dict(
        self,
    ) -> Mapping[str, object]:
        evaluation = dict(
            self.evaluation.to_safe_dict()
        )

        return MappingProxyType(
            {
                "operation": self.operation,
                "source": self.source.value,
                "shared_data_used": (
                    self.shared_data_used
                ),
                "provider_enabled": (
                    self.provider_enabled
                ),
                "cache_age_seconds": (
                    self.cache_age_seconds
                ),
                "cache_stale": (
                    self.cache_stale
                ),
                "database_unavailable": (
                    self.database_unavailable
                ),
                "refresh_in_flight": (
                    self.refresh_in_flight
                ),
                "evaluation": (
                    MappingProxyType(
                        evaluation
                    )
                ),
            }
        )


def _window_seconds_match(
    left: float,
    right: float,
) -> bool:
    return math.isclose(
        float(left),
        float(right),
        rel_tol=1e-12,
        abs_tol=1e-12,
    )


def evaluate_distributed_reliability(
    shared_snapshot: SharedReliabilitySnapshot,
) -> DistributedReliabilitySnapshot:
    """
    Transforma uma leitura do Shared Provider em
    uma avaliação operacional efetiva.

    Nenhuma consulta PostgreSQL ocorre aqui.
    """
    if not isinstance(
        shared_snapshot,
        SharedReliabilitySnapshot,
    ):
        raise TypeError(
            "shared_snapshot must be a "
            "SharedReliabilitySnapshot."
        )

    operation = str(
        shared_snapshot.operation
    ).strip()

    policy = (
        PRODUCTION_RELIABILITY_POLICIES
        .get(operation)
    )

    if policy is None:
        raise ValueError(
            "Operation is not a tracked "
            "production reliability boundary."
        )

    local_snapshot = (
        shared_snapshot.local_snapshot
    )

    if not isinstance(
        local_snapshot,
        ProductionReliabilitySnapshot,
    ):
        raise TypeError(
            "local_snapshot must be a "
            "ProductionReliabilitySnapshot."
        )

    if (
        local_snapshot.operation
        != operation
    ):
        raise ValueError(
            "Local reliability snapshot "
            "operation mismatch."
        )

    use_shared = (
        shared_snapshot.source
        is ReliabilityDataSource.SHARED_CACHE
    )

    if use_shared:
        window = (
            shared_snapshot.shared_window
        )

        if window is None:
            raise ValueError(
                "Shared cache source requires "
                "a shared reliability window."
            )

        if window.operation != operation:
            raise ValueError(
                "Shared reliability window "
                "operation mismatch."
            )

        if not _window_seconds_match(
            window.window_seconds,
            policy.window_seconds,
        ):
            raise ValueError(
                "Shared reliability window "
                "does not match the production "
                "policy window."
            )

        evaluation = (
            evaluate_production_reliability_counts(
                policy=policy,
                total_operations=(
                    window.total_operations
                ),
                successful_operations=(
                    window.successful_operations
                ),
                failed_operations=(
                    window.failed_operations
                ),
                circuit_rejections=(
                    window.circuit_rejections
                ),
            )
        )

    else:
        if (
            shared_snapshot.shared_window
            is not None
        ):
            raise ValueError(
                "Local fallback must not expose "
                "a shared reliability window."
            )

        evaluation = local_snapshot

    return DistributedReliabilitySnapshot(
        operation=operation,
        source=shared_snapshot.source,
        evaluation=evaluation,
        shared_data_used=use_shared,
        provider_enabled=(
            shared_snapshot.provider_enabled
        ),
        cache_age_seconds=(
            shared_snapshot.cache_age_seconds
        ),
        cache_stale=(
            shared_snapshot.cache_stale
        ),
        database_unavailable=(
            shared_snapshot.database_unavailable
        ),
        refresh_in_flight=(
            shared_snapshot.refresh_in_flight
        ),
    )


def get_distributed_reliability_snapshot(
    operation: str,
    *,
    provider: SharedReliabilityProvider | None = None,
) -> DistributedReliabilitySnapshot:
    """
    Superfície prevista para o futuro Governor.

    O próprio método não consulta banco diretamente.
    SharedReliabilityProvider.snapshot() retorna
    cache/fallback e agenda refresh quando necessário.
    """
    active_provider = (
        provider
        or get_shared_reliability_provider()
    )

    shared_snapshot = (
        active_provider.snapshot(
            operation
        )
    )

    return evaluate_distributed_reliability(
        shared_snapshot
    )


__all__ = [
    "DistributedReliabilitySnapshot",
    "evaluate_distributed_reliability",
    "get_distributed_reliability_snapshot",
]
