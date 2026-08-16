from __future__ import annotations

from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel

from api.security import (
    TrustedRequestContext,
    require_trusted_request_context,
)
from src.reliability.distributed_evaluation import (
    evaluate_distributed_reliability,
)
from src.reliability.shared_provider import (
    get_shared_reliability_provider,
)

router = APIRouter()


ReliabilityOperation = Literal[
    "gemini.embedding",
    "gemini.generate.supervisor",
    "gemini.generate.text_service",
    "rag.agentic.planner",
]


class SharedReliabilityDiagnosticRequest(
    BaseModel
):
    operation: ReliabilityOperation


class SharedReliabilityDiagnosticResponse(
    BaseModel
):
    operation: str
    provider_enabled: bool
    refresh_succeeded: bool
    source: str
    shared_data_used: bool
    state: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    circuit_rejections: int
    cache_stale: bool
    database_unavailable: bool
    refresh_in_flight: bool


@router.post(
    (
        "/internal/reliability/"
        "shared-provider/refresh"
    ),
    response_model=(
        SharedReliabilityDiagnosticResponse
    ),
    include_in_schema=False,
)
def refresh_shared_reliability_provider(
    payload: SharedReliabilityDiagnosticRequest,
    _trusted_context: Annotated[
        TrustedRequestContext,
        Depends(
            require_trusted_request_context
        ),
    ],
) -> SharedReliabilityDiagnosticResponse:
    """
    Diagnóstico interno e autenticado.

    Executa refresh explícito do Shared
    Reliability Provider e retorna somente
    metadados operacionais privacy-safe.

    Não altera políticas do Governor.
    """
    try:
        provider = (
            get_shared_reliability_provider()
        )

        refresh_succeeded = (
            provider.refresh_now(
                payload.operation
            )
        )

        shared_snapshot = provider.snapshot(
            payload.operation
        )

        distributed = (
            evaluate_distributed_reliability(
                shared_snapshot
            )
        )

        evaluation = distributed.evaluation

        return (
            SharedReliabilityDiagnosticResponse(
                operation=payload.operation,
                provider_enabled=(
                    distributed.provider_enabled
                ),
                refresh_succeeded=(
                    refresh_succeeded
                ),
                source=distributed.source.value,
                shared_data_used=(
                    distributed.shared_data_used
                ),
                state=evaluation.state.value,
                total_operations=(
                    evaluation.total_operations
                ),
                successful_operations=(
                    evaluation.successful_operations
                ),
                failed_operations=(
                    evaluation.failed_operations
                ),
                circuit_rejections=(
                    evaluation.circuit_rejections
                ),
                cache_stale=(
                    distributed.cache_stale
                ),
                database_unavailable=(
                    distributed.database_unavailable
                ),
                refresh_in_flight=(
                    distributed.refresh_in_flight
                ),
            )
        )

    except Exception:
        # Nenhum detalhe interno, segredo,
        # DSN ou erro PostgreSQL é exposto.
        raise HTTPException(
            status_code=503,
            detail=(
                "Diagnóstico de reliability "
                "indisponível."
            ),
        ) from None


__all__ = [
    "router",
]
