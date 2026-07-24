from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from api.human_review_schemas import (
    HumanReviewDecisionRequest,
    HumanReviewListResponse,
    HumanReviewRecordResponse,
    HumanReviewRecoveryRequest,
    HumanReviewRecoveryResponse,
    HumanReviewRegisterRequest,
    HumanReviewResolutionResponse,
    HumanReviewWriteResponse,
)

from api.security.internal_request import (
    TrustedRequestContext,
    require_trusted_request_context,
)

from src.services.human_review import service

from src.services.human_review.exceptions import (
    HumanReviewConflictError,
    HumanReviewNotFoundError,
    HumanReviewRepositoryError,
    HumanReviewResumeError,
    HumanReviewServiceError,
    HumanReviewValidationError,
)


router = APIRouter(
    prefix="/internal/human-reviews",
    tags=[
        "Human-in-the-Loop",
    ],
)


TrustedContextDependency = Annotated[
    TrustedRequestContext,
    Depends(
        require_trusted_request_context
    ),
]


def _raise_http_error(
    exc: Exception,
) -> None:
    if isinstance(
        exc,
        HumanReviewValidationError,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from None

    if isinstance(
        exc,
        HumanReviewNotFoundError,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from None

    if isinstance(
        exc,
        HumanReviewConflictError,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(exc),
        ) from None

    if isinstance(
        exc,
        HumanReviewResumeError,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "Não foi possível concluir a "
                "retomada da revisão humana."
            ),
        ) from None

    if isinstance(
        exc,
        HumanReviewRepositoryError,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "O serviço de revisões humanas "
                "está temporariamente indisponível."
            ),
        ) from None

    if isinstance(
        exc,
        HumanReviewServiceError,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Não foi possível processar a "
                "revisão humana."
            ),
        ) from None

    raise HTTPException(
        status_code=(
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
        detail=(
            "Erro interno ao processar a revisão "
            "humana."
        ),
    ) from None


@router.post(
    "/register",
    response_model=HumanReviewWriteResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_human_review(
    payload: HumanReviewRegisterRequest,
    _: TrustedContextDependency,
) -> HumanReviewWriteResponse:
    try:
        result = (
            service
            .registrar_revisao_pendente(
                payload.model_dump(
                    mode="python",
                )
            )
        )

        return HumanReviewWriteResponse(
            **result.to_dict()
        )

    except Exception as exc:
        _raise_http_error(
            exc
        )


@router.get(
    "/pending",
    response_model=HumanReviewListResponse,
)
def list_pending_human_reviews(
    _: TrustedContextDependency,
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> HumanReviewListResponse:
    try:
        records = (
            service
            .listar_revisoes_pendentes(
                limit=limit,
                offset=offset,
            )
        )

        return HumanReviewListResponse(
            items=[
                HumanReviewRecordResponse(
                    **record.model_dump(
                        mode="python",
                    )
                )
                for record in records
            ],
            count=len(records),
            limit=limit,
            offset=offset,
        )

    except Exception as exc:
        _raise_http_error(
            exc
        )


@router.post(
    "/recover-stale",
    response_model=HumanReviewRecoveryResponse,
)
def recover_stale_human_reviews(
    payload: HumanReviewRecoveryRequest,
    _: TrustedContextDependency,
) -> HumanReviewRecoveryResponse:
    try:
        recovered = (
            service
            .recuperar_claims_expirados(
                timeout_seconds=(
                    payload.timeout_seconds
                ),
            )
        )

        return HumanReviewRecoveryResponse(
            recovered_review_ids=recovered,
            recovered_count=len(
                recovered
            ),
        )

    except Exception as exc:
        _raise_http_error(
            exc
        )


@router.get(
    "/{review_id}",
    response_model=HumanReviewRecordResponse,
)
def get_human_review(
    review_id: str,
    _: TrustedContextDependency,
) -> HumanReviewRecordResponse:
    try:
        record = (
            service
            .consultar_revisao(
                review_id
            )
        )

        return HumanReviewRecordResponse(
            **record.model_dump(
                mode="python",
            )
        )

    except Exception as exc:
        _raise_http_error(
            exc
        )


@router.post(
    "/{review_id}/resolve",
    response_model=HumanReviewResolutionResponse,
)
def resolve_human_review(
    review_id: str,
    payload: HumanReviewDecisionRequest,
    context: TrustedContextDependency,
) -> HumanReviewResolutionResponse:
    try:
        outcome = (
            service
            .resolver_revisao_humana(
                review_id=review_id,
                thread_id=(
                    payload.thread_id
                ),
                trusted_reviewer_id=(
                    context.user_id
                ),
                request_id=(
                    context.request_id
                ),
                decision_payload={
                    "action": payload.action,
                    "comment": payload.comment,
                    "reason": payload.reason,
                    "corrections": (
                        payload.corrections
                    ),
                },
            )
        )

        return HumanReviewResolutionResponse(
            **outcome.to_dict()
        )

    except Exception as exc:
        _raise_http_error(
            exc
        )


__all__ = [
    "router",
]
