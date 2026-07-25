from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from api.human_review_schemas import (
    HumanReviewAdminMetricsResponse,
    HumanReviewAdminPageResponse,
    HumanReviewRecordResponse,
    HumanReviewRecoveryRequest,
    HumanReviewRecoveryResponse,
)
from api.security.human_review_admin import (
    HumanReviewAdminContextDependency,
)
from src.services.human_review import service
from src.services.human_review.admin_contracts import (
    HumanReviewAdminFilters,
)
from src.services.human_review.admin_queries import (
    listar_revisoes_admin,
    obter_metricas_admin,
)
from src.services.human_review.exceptions import (
    HumanReviewNotFoundError,
    HumanReviewRepositoryError,
    HumanReviewServiceError,
    HumanReviewValidationError,
)


router = APIRouter(
    prefix="/internal/human-reviews/admin",
    tags=["human-review-admin"],
)


StatusFilter = Annotated[
    list[str] | None,
    Query(),
]

RiskFilter = Annotated[
    list[str] | None,
    Query(),
]


def _raise_admin_http_error(
    exc: Exception,
) -> None:
    if isinstance(
        exc,
        (
            HumanReviewValidationError,
            ValueError,
        ),
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc

    if isinstance(
        exc,
        HumanReviewNotFoundError,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Revisão humana não encontrada.",
        ) from exc

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
        ) from exc

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
                "operação administrativa."
            ),
        ) from exc

    raise HTTPException(
        status_code=(
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
        detail=(
            "Erro interno na operação "
            "administrativa HITL."
        ),
    ) from exc


def _start_of_day(
    value: datetime | None,
) -> datetime | None:
    if value is None:
        return None

    return value.astimezone(UTC)


@router.get(
    "/reviews",
    response_model=HumanReviewAdminPageResponse,
)
def list_admin_human_reviews(
    _: HumanReviewAdminContextDependency,
    statuses: StatusFilter = None,
    risk_levels: RiskFilter = None,
    requested_by: str = Query(
        default="",
        max_length=160,
    ),
    reviewer_id: str = Query(
        default="",
        max_length=160,
    ),
    thread_id: str = Query(
        default="",
        max_length=200,
    ),
    search: str = Query(
        default="",
        max_length=300,
    ),
    created_from: datetime | None = Query(
        default=None,
    ),
    created_to: datetime | None = Query(
        default=None,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> HumanReviewAdminPageResponse:
    try:
        filters = HumanReviewAdminFilters(
            statuses=tuple(statuses or ()),
            risk_levels=tuple(
                risk_levels or ()
            ),
            requested_by=requested_by.strip(),
            reviewer_id=reviewer_id.strip(),
            thread_id=thread_id.strip(),
            created_from=_start_of_day(
                created_from
            ),
            created_to=_start_of_day(
                created_to
            ),
            search=search.strip(),
            limit=limit,
            offset=offset,
        )

        page = listar_revisoes_admin(
            filters
        )

        return HumanReviewAdminPageResponse(
            items=[
                HumanReviewRecordResponse(
                    **item
                )
                for item in page.items
            ],
            total=page.total,
            limit=page.limit,
            offset=page.offset,
            has_next=page.has_next,
            has_previous=page.has_previous,
        )

    except Exception as exc:
        _raise_admin_http_error(exc)


@router.get(
    "/reviews/{review_id}",
    response_model=HumanReviewRecordResponse,
)
def get_admin_human_review(
    review_id: str,
    _: HumanReviewAdminContextDependency,
) -> HumanReviewRecordResponse:
    try:
        record = service.consultar_revisao(
            review_id
        )

        return HumanReviewRecordResponse(
            **record.model_dump(
                mode="python"
            )
        )

    except Exception as exc:
        _raise_admin_http_error(exc)


@router.get(
    "/metrics",
    response_model=HumanReviewAdminMetricsResponse,
)
def get_admin_human_review_metrics(
    _: HumanReviewAdminContextDependency,
    created_from: datetime | None = Query(
        default=None,
    ),
    created_to: datetime | None = Query(
        default=None,
    ),
) -> HumanReviewAdminMetricsResponse:
    try:
        metrics = obter_metricas_admin(
            created_from=_start_of_day(
                created_from
            ),
            created_to=_start_of_day(
                created_to
            ),
        )

        return HumanReviewAdminMetricsResponse(
            **metrics.to_dict()
        )

    except Exception as exc:
        _raise_admin_http_error(exc)


@router.post(
    "/recover-stale",
    response_model=HumanReviewRecoveryResponse,
)
def recover_admin_stale_human_reviews(
    payload: HumanReviewRecoveryRequest,
    _: HumanReviewAdminContextDependency,
) -> HumanReviewRecoveryResponse:
    try:
        recovered = (
            service
            .recuperar_claims_expirados(
                timeout_seconds=(
                    payload.timeout_seconds
                )
            )
        )

        return HumanReviewRecoveryResponse(
            recovered_review_ids=recovered,
            recovered_count=len(recovered),
        )

    except Exception as exc:
        _raise_admin_http_error(exc)

