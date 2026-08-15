"""Governor advisory da Reliability de produção da INNA."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from enum import StrEnum
from types import MappingProxyType

from src.resilience.contracts import (
    OperationKind,
    ResiliencePolicy,
)
from src.resilience.policies import (
    AGENTIC_RAG_PLANNER_POLICY,
    GEMINI_EMBEDDING_POLICY,
    GEMINI_TEXT_GENERATION_POLICY,
    SUPERVISOR_GENERATION_POLICY,
)

from .distributed_evaluation import (
    DistributedReliabilitySnapshot,
    get_distributed_reliability_snapshot,
)
from .production_tracker import (
    OperationalReliabilityState,
)
from .shared_provider import (
    ReliabilityDataSource,
)


class ReliabilityGovernorAction(StrEnum):
    KEEP_CURRENT = "keep_current"
    REDUCE_RETRIES = "reduce_retries"
    CONSERVATIVE_MODE = "conservative_mode"


GOVERNED_RESILIENCE_POLICIES = MappingProxyType(
    {
        GEMINI_EMBEDDING_POLICY.name: (
            GEMINI_EMBEDDING_POLICY
        ),
        GEMINI_TEXT_GENERATION_POLICY.name: (
            GEMINI_TEXT_GENERATION_POLICY
        ),
        SUPERVISOR_GENERATION_POLICY.name: (
            SUPERVISOR_GENERATION_POLICY
        ),
        AGENTIC_RAG_PLANNER_POLICY.name: (
            AGENTIC_RAG_PLANNER_POLICY
        ),
    }
)


# Somente fallback explicitamente comprovado
# no discovery 3F.1.
_EXPLICIT_SAFE_FALLBACK_OPERATIONS = frozenset(
    {
        "rag.agentic.planner",
    }
)


@dataclass(
    frozen=True,
    slots=True,
)
class ReliabilityGovernorDecision:
    operation: str
    action: ReliabilityGovernorAction
    reason_code: str

    advisory_only: bool

    source: ReliabilityDataSource
    state: OperationalReliabilityState

    shared_data_used: bool
    cache_stale: bool
    database_unavailable: bool

    current_max_attempts: int
    recommended_max_attempts: int

    prefer_fallback: bool

    burn_rate: float | None

    def to_safe_dict(
        self,
    ) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "operation": self.operation,
                "action": self.action.value,
                "reason_code": self.reason_code,
                "advisory_only": (
                    self.advisory_only
                ),
                "source": self.source.value,
                "state": self.state.value,
                "shared_data_used": (
                    self.shared_data_used
                ),
                "cache_stale": (
                    self.cache_stale
                ),
                "database_unavailable": (
                    self.database_unavailable
                ),
                "current_max_attempts": (
                    self.current_max_attempts
                ),
                "recommended_max_attempts": (
                    self.recommended_max_attempts
                ),
                "prefer_fallback": (
                    self.prefer_fallback
                ),
                "burn_rate": self.burn_rate,
            }
        )


def advise_reliability_governor(
    *,
    policy: ResiliencePolicy,
    snapshot: DistributedReliabilitySnapshot,
) -> ReliabilityGovernorDecision:
    """
    Produz recomendação determinística.

    Não:
    - muta ResiliencePolicy;
    - chama PostgreSQL diretamente;
    - altera ResilienceRuntime;
    - executa fallback;
    - altera retries reais.
    """
    if not isinstance(
        policy,
        ResiliencePolicy,
    ):
        raise TypeError(
            "policy must be a ResiliencePolicy."
        )

    if not isinstance(
        snapshot,
        DistributedReliabilitySnapshot,
    ):
        raise TypeError(
            "snapshot must be a "
            "DistributedReliabilitySnapshot."
        )

    if policy.name != snapshot.operation:
        raise ValueError(
            "Policy and reliability snapshot "
            "operation mismatch."
        )

    if (
        policy.name
        not in GOVERNED_RESILIENCE_POLICIES
    ):
        raise ValueError(
            "Operation is not governed by "
            "production Reliability."
        )

    source_is_shared = (
        snapshot.source
        is ReliabilityDataSource.SHARED_CACHE
    )

    if (
        snapshot.shared_data_used
        != source_is_shared
    ):
        raise ValueError(
            "Distributed reliability source "
            "metadata is inconsistent."
        )

    current_attempts = int(
        policy.max_attempts
    )

    action = (
        ReliabilityGovernorAction
        .KEEP_CURRENT
    )

    recommended_attempts = (
        current_attempts
    )

    prefer_fallback = False


    # Dados apenas locais nunca provocam uma
    # ação global agressiva.
    if not snapshot.shared_data_used:
        reason_code = (
            "local_fallback_no_aggressive_action"
        )

    # Amostra insuficiente também não provoca
    # redução automática.
    elif (
        snapshot.state
        is OperationalReliabilityState
        .INSUFFICIENT_DATA
    ):
        reason_code = (
            "insufficient_data_no_aggressive_action"
        )

    elif (
        snapshot.state
        is OperationalReliabilityState
        .HEALTHY
    ):
        reason_code = (
            "shared_healthy_keep_current"
        )

    elif (
        snapshot.state
        is OperationalReliabilityState
        .DEGRADED
    ):
        action = (
            ReliabilityGovernorAction
            .REDUCE_RETRIES
        )

        recommended_attempts = max(
            1,
            current_attempts - 1,
        )

        reason_code = (
            "shared_degraded_reduce_retries"
        )

    elif (
        snapshot.state
        is OperationalReliabilityState
        .CRITICAL
    ):
        action = (
            ReliabilityGovernorAction
            .CONSERVATIVE_MODE
        )

        recommended_attempts = 1

        prefer_fallback = (
            policy.name
            in _EXPLICIT_SAFE_FALLBACK_OPERATIONS
        )

        reason_code = (
            "shared_critical_conservative_mode"
        )

    else:
        raise ValueError(
            "Unsupported operational "
            "reliability state."
        )


    # O Governor advisory nunca pode sugerir
    # MAIS tentativas do que a policy original.
    if (
        recommended_attempts
        > current_attempts
    ):
        raise RuntimeError(
            "Governor recommendation cannot "
            "expand retry attempts."
        )


    return ReliabilityGovernorDecision(
        operation=policy.name,
        action=action,
        reason_code=reason_code,
        advisory_only=True,
        source=snapshot.source,
        state=snapshot.state,
        shared_data_used=(
            snapshot.shared_data_used
        ),
        cache_stale=(
            snapshot.cache_stale
        ),
        database_unavailable=(
            snapshot.database_unavailable
        ),
        current_max_attempts=(
            current_attempts
        ),
        recommended_max_attempts=(
            recommended_attempts
        ),
        prefer_fallback=(
            prefer_fallback
        ),
        burn_rate=snapshot.burn_rate,
    )



def derive_effective_resilience_policy(
    *,
    policy: ResiliencePolicy,
    decision: ReliabilityGovernorDecision,
) -> ResiliencePolicy:
    """
    Deriva uma policy imutável a partir de uma
    decisão advisory já validada.

    Esta função não:
    - muta a policy original;
    - altera o ResilienceRuntime;
    - executa fallback;
    - consulta banco;
    - aumenta retries.
    """
    if not isinstance(
        policy,
        ResiliencePolicy,
    ):
        raise TypeError(
            "policy must be a ResiliencePolicy."
        )

    if not isinstance(
        decision,
        ReliabilityGovernorDecision,
    ):
        raise TypeError(
            "decision must be a "
            "ReliabilityGovernorDecision."
        )

    governed_policy = (
        GOVERNED_RESILIENCE_POLICIES
        .get(policy.name)
    )

    if governed_policy is None:
        raise ValueError(
            "Operation is not governed by "
            "production Reliability."
        )

    # A derivação deve partir da policy real
    # registrada, não de uma configuração
    # arbitrária que reutilize o mesmo nome.
    if policy != governed_policy:
        raise ValueError(
            "Policy does not match the governed "
            "production policy."
        )

    if decision.operation != policy.name:
        raise ValueError(
            "Policy and Governor decision "
            "operation mismatch."
        )

    current_attempts = int(
        policy.max_attempts
    )

    if (
        decision.current_max_attempts
        != current_attempts
    ):
        raise ValueError(
            "Governor decision current attempts "
            "do not match the base policy."
        )

    recommended = int(
        decision.recommended_max_attempts
    )

    if recommended < 1:
        raise ValueError(
            "Recommended max_attempts must be "
            "at least 1."
        )

    if recommended > current_attempts:
        raise ValueError(
            "Governor cannot expand retry "
            "attempts."
        )

    if (
        decision.action
        is ReliabilityGovernorAction
        .KEEP_CURRENT
    ):
        if recommended != current_attempts:
            raise ValueError(
                "KEEP_CURRENT must preserve "
                "max_attempts."
            )

        return policy

    # Qualquer redução exige dados compartilhados.
    if (
        not decision.shared_data_used
        or decision.source
        is not ReliabilityDataSource
        .SHARED_CACHE
    ):
        raise ValueError(
            "Retry reduction requires shared "
            "Reliability data."
        )

    # Nunca reduzimos/alteramos automaticamente
    # policies side-effecting.
    if (
        policy.operation_kind
        is OperationKind.SIDE_EFFECT
    ):
        raise ValueError(
            "Governor cannot derive retry "
            "changes for side-effect operations."
        )

    if (
        decision.state
        is OperationalReliabilityState
        .INSUFFICIENT_DATA
    ):
        raise ValueError(
            "Insufficient data cannot derive "
            "a reduced retry policy."
        )

    if (
        decision.state
        is OperationalReliabilityState
        .HEALTHY
    ):
        raise ValueError(
            "Healthy state cannot derive "
            "a reduced retry policy."
        )

    if (
        decision.action
        is ReliabilityGovernorAction
        .REDUCE_RETRIES
    ):
        expected = max(
            1,
            current_attempts - 1,
        )

        if recommended != expected:
            raise ValueError(
                "REDUCE_RETRIES recommendation "
                "does not match Governor rules."
            )

    elif (
        decision.action
        is ReliabilityGovernorAction
        .CONSERVATIVE_MODE
    ):
        if recommended != 1:
            raise ValueError(
                "CONSERVATIVE_MODE must derive "
                "max_attempts=1."
            )

    else:
        raise ValueError(
            "Unsupported Governor action."
        )

    if recommended == current_attempts:
        return policy

    return replace(
        policy,
        max_attempts=recommended,
    )



def get_reliability_governor_decision(
    operation: str,
    *,
    snapshot: (
        DistributedReliabilitySnapshot
        | None
    ) = None,
) -> ReliabilityGovernorDecision:
    """
    Superfície advisory.

    Quando snapshot não é fornecido, usa a
    camada Distributed Reliability existente.
    """
    normalized = str(
        operation
    ).strip()

    policy = (
        GOVERNED_RESILIENCE_POLICIES
        .get(normalized)
    )

    if policy is None:
        raise ValueError(
            "Operation is not governed by "
            "production Reliability."
        )

    active_snapshot = (
        snapshot
        if snapshot is not None
        else get_distributed_reliability_snapshot(
            normalized
        )
    )

    return advise_reliability_governor(
        policy=policy,
        snapshot=active_snapshot,
    )


__all__ = [
    "GOVERNED_RESILIENCE_POLICIES",
    "ReliabilityGovernorAction",
    "ReliabilityGovernorDecision",
    "advise_reliability_governor",
    "derive_effective_resilience_policy",
    "get_reliability_governor_decision",
]
