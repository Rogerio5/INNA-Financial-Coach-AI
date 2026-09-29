from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from functools import lru_cache
from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header,
    Path,
    Query,
    status,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from src.inna_platform.services.finance.finance_access_gate import (
    get_financeiro_entitled_user,
)

from .agent.agent import ReimbursementAgent
from .agent.policy_engine import ReimbursementPolicyEngine
from .policy.repository import (
    PostgresReimbursementPolicyRepository,
)

from .auto_approval.repository import (
    PostgresAutoApprovalConfigurationRepository,
)

from .audit.audit_service import (
    PostgresReimbursementAuditService,
    ReimbursementAuditService,
)

from .corporate.context import (
    CorporateContext,
    resolve_corporate_context,
)

from .corporate.rbac import (
    can_review_reimbursements,
)

from .corporate.repository import (
    CorporateRepository,
    PostgresCorporateRepository,
)

from .db_schema import (
    ensure_reimbursement_schema,
    reimbursement_database_capabilities,
)

from .hitl.review_service import (
    HumanReviewService,
)

from .models import (
    ReimbursementRequest,
    ReimbursementStatus,
)

from .repository import (
    PostgresReimbursementRepository,
    ReimbursementRepository,
)

from .schemas import (
    HumanReviewInput,
    ReimbursementCreate,
)

from .service import (
    ReimbursementService,
)


router = APIRouter(
    prefix="/api/platform/finance/reimbursements",
    tags=["Finance Reimbursements"],
)


REIMBURSEMENT_HUMAN_REVIEW_API_ENABLED = True


class ReimbursementCreateRequest(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
    )

    amount: int = Field(
        ge=1,
    )

    currency: str = Field(
        default="BRL",
        min_length=3,
        max_length=3,
    )

    category: str = Field(
        min_length=1,
        max_length=120,
    )

    description: str = Field(
        min_length=1,
        max_length=1000,
    )

    merchant: str | None = Field(
        default=None,
        max_length=200,
    )

    expense_date: date | None = None

    receipt_reference: str | None = Field(
        default=None,
        max_length=500,
    )


class ReimbursementReviewRequest(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
    )

    decision: Literal[
        "approve",
        "reject",
        "request_information",
    ]

    reason: str = Field(
        min_length=1,
        max_length=1000,
    )


@dataclass
class ReimbursementRuntime:
    repository: ReimbursementRepository

    audit: (
        ReimbursementAuditService
        |
        PostgresReimbursementAuditService
    )

    service: ReimbursementService
    reviewer: HumanReviewService

    corporate_repository: CorporateRepository
@lru_cache(maxsize=1)
def _persistent_runtime() -> ReimbursementRuntime:

    ensure_reimbursement_schema()

    repository = (
        PostgresReimbursementRepository()
    )

    audit = (
        PostgresReimbursementAuditService()
    )

    corporate_repository = (
        PostgresCorporateRepository()
    )

    agent = ReimbursementAgent(
        policy_engine=
            ReimbursementPolicyEngine(
                repository=
                    PostgresReimbursementPolicyRepository()
            )
    )

    service = ReimbursementService(
        repository=repository,
        audit=audit,
        agent=agent,
            auto_approval_repository=
            PostgresAutoApprovalConfigurationRepository(),

)

    reviewer = HumanReviewService(
        repository=repository,
        audit=audit,
    )

    return ReimbursementRuntime(
        repository=repository,
        audit=audit,
        service=service,
        reviewer=reviewer,
        corporate_repository=
            corporate_repository,
    )


def get_reimbursement_runtime() -> ReimbursementRuntime:
    return _persistent_runtime()


def _user_id_from_user(
    user: dict,
) -> str:

    user_id = str(
        user.get(
            "user_id",
            "",
        )
    ).strip()

    if not user_id:

        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,

            detail=
                "Identidade autenticada inválida",
        )

    return user_id


def _corporate_context_from_user(
    *,
    user: dict,
    runtime: ReimbursementRuntime,
) -> CorporateContext:

    user_id = _user_id_from_user(
        user
    )

    try:

        context = resolve_corporate_context(
            repository=
                runtime.corporate_repository,

            user_id=user_id,
        )

    except ValueError as exc:

        if (
            str(exc)
            ==
            "MULTIPLE_ORGANIZATIONS_REQUIRE_SELECTION"
        ):

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,

                detail=(
                    "Usuário pertence a mais de uma "
                    "organização. A seleção explícita "
                    "de empresa ainda precisa ser feita."
                ),
            ) from exc

        raise

    if context is None:

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "ORGANIZATION_MEMBERSHIP_REQUIRED",
        )

    return context


def _serialize_request(
    reimbursement: ReimbursementRequest,
) -> dict:

    payload = asdict(
        reimbursement
    )

    payload["status"] = (
        reimbursement.status.value
    )

    payload["created_at"] = (
        reimbursement.created_at
        .isoformat()
    )

    payload["updated_at"] = (
        reimbursement.updated_at
        .isoformat()
    )

    return payload


def _require_owned_request(
    *,
    runtime: ReimbursementRuntime,
    organization_id: str,
    user_id: str,
    reimbursement_id: str,
) -> ReimbursementRequest:

    reimbursement = (
        runtime.repository.get(
            tenant_id=organization_id,
            reimbursement_id=
                reimbursement_id,
        )
    )

    if reimbursement is None:

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "Reembolso não encontrado",
        )

    if reimbursement.user_id != user_id:

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "Reembolso não encontrado",
        )

    return reimbursement


def _require_organization_request(
    *,
    runtime: ReimbursementRuntime,
    organization_id: str,
    reimbursement_id: str,
) -> ReimbursementRequest:

    reimbursement = (
        runtime.repository.get(
            tenant_id=organization_id,
            reimbursement_id=
                reimbursement_id,
        )
    )

    if reimbursement is None:

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "Reembolso não encontrado",
        )

    return reimbursement


@router.get(
    "/capabilities",
)
def reimbursement_capabilities(
    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReimbursementRuntime = Depends(
        get_reimbursement_runtime
    ),
):

    context = (
        _corporate_context_from_user(
            user=user,
            runtime=runtime,
        )
    )

    database = (
        reimbursement_database_capabilities()
    )

    return {
        "ok": True,

        "version":
            "reimbursement-1b3b",

        "authenticated":
            True,

        "organization_id":
            context.organization_id,

        "organization_role":
            context.member.role.value,

        "user_id":
            context.user_id,

        "tenant_identity_source":
            "organization_membership",

        "browser_user_id_allowed":
            False,

        "browser_tenant_id_allowed":
            False,

        "browser_role_assignment":
            False,

        "persistent_requests":
            database[
                "persistent_requests"
            ],

        "persistent_audit":
            database[
                "persistent_audit"
            ],

        "human_review_required":
            True,

        "human_review_api_enabled":
            True,

        "can_review":
            can_review_reimbursements(
                context.member
            ),

        "automatic_approval":
            False,

        "self_approval":
            False,
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_reimbursement(
    payload: ReimbursementCreateRequest,

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReimbursementRuntime = Depends(
        get_reimbursement_runtime
    ),
):

    context = (
        _corporate_context_from_user(
            user=user,
            runtime=runtime,
        )
    )

    internal = ReimbursementCreate(
        tenant_id=
            context.organization_id,

        user_id=
            context.user_id,

        amount=
            payload.amount,

        currency=
            payload.currency
            .strip()
            .upper(),

        category=
            payload.category
            .strip(),

        description=
            payload.description
            .strip(),

        merchant=(
            payload.merchant.strip()
            if payload.merchant
            else None
        ),

        expense_date=(
            payload.expense_date
            .isoformat()
            if payload.expense_date
            else None
        ),

        receipt_reference=(
            payload.receipt_reference
            .strip()
            if payload.receipt_reference
            else None
        ),

        source_type="finance",
        source_reference=None,
    )

    reimbursement = (
        runtime.service.create(
            internal
        )
    )

    return {
        "ok": True,

        "reimbursement":
            _serialize_request(
                reimbursement
            ),
    }


@router.get(
    "",
)
def list_reimbursements(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReimbursementRuntime = Depends(
        get_reimbursement_runtime
    ),
):

    context = (
        _corporate_context_from_user(
            user=user,
            runtime=runtime,
        )
    )

    items = (
        runtime.repository
        .list_by_user(
            tenant_id=
                context.organization_id,

            user_id=
                context.user_id,
        )
    )

    items = items[:limit]

    return {
        "ok": True,

        "count":
            len(items),

        "reimbursements": [
            _serialize_request(item)
            for item in items
        ],
    }



# SABINO_REIMBURSEMENT_PHASE_1B3C_QUEUE_START


def _require_reviewer_context(
    *,
    user: dict,
    runtime: ReimbursementRuntime,
) -> CorporateContext:

    context = (
        _corporate_context_from_user(
            user=user,
            runtime=runtime,
        )
    )

    if not can_review_reimbursements(
        context.member
    ):

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "REIMBURSEMENT_REVIEW_FORBIDDEN",
        )

    return context


def _review_queue_items(
    *,
    runtime: ReimbursementRuntime,
    organization_id: str,
    reviewer_user_id: str,
    limit: int,
) -> list[ReimbursementRequest]:

    from .models import (
        ReimbursementStatus,
    )

    list_by_tenant = getattr(
        runtime.repository,
        "list_by_tenant",
        None,
    )

    if not callable(
        list_by_tenant
    ):

        raise HTTPException(
            status_code=
                status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=
                "REIMBURSEMENT_REVIEW_QUEUE_UNAVAILABLE",
        )

    #
    # Busca somente itens aguardando decisão humana.
    #
    candidates = list_by_tenant(
        tenant_id=
            organization_id,

        status=
            ReimbursementStatus
            .AWAITING_HUMAN_REVIEW,

        limit=
            min(
                max(
                    int(limit) * 3,
                    50,
                ),
                500,
            ),
    )

    #
    # Segregação de função:
    # o próprio pedido nunca aparece
    # na fila do aprovador.
    #
    visible = [
        item
        for item
        in candidates
        if (
            item.user_id
            != reviewer_user_id
        )
    ]

    return visible[
        :limit
    ]


@router.get(
    "/review-queue",
)
def list_reimbursement_review_queue(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReimbursementRuntime = Depends(
        get_reimbursement_runtime
    ),
):

    context = (
        _require_reviewer_context(
            user=user,
            runtime=runtime,
        )
    )

    items = (
        _review_queue_items(
            runtime=runtime,

            organization_id=
                context.organization_id,

            reviewer_user_id=
                context.user_id,

            limit=limit,
        )
    )

    return {
        "ok":
            True,

        "organization_id":
            context.organization_id,

        "reviewer_user_id":
            context.user_id,

        "reviewer_role":
            context.member.role.value,

        "count":
            len(items),

        "queue": [
            _serialize_request(
                item
            )
            for item
            in items
        ],
    }


@router.get(
    "/review-queue/{reimbursement_id}",
)
def get_reimbursement_review_queue_item(
    reimbursement_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReimbursementRuntime = Depends(
        get_reimbursement_runtime
    ),
):

    context = (
        _require_reviewer_context(
            user=user,
            runtime=runtime,
        )
    )

    reimbursement = (
        _require_organization_request(
            runtime=runtime,

            organization_id=
                context.organization_id,

            reimbursement_id=
                reimbursement_id,
        )
    )

    if (
        reimbursement.user_id
        ==
        context.user_id
    ):

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "SELF_REVIEW_QUEUE_FORBIDDEN",
        )

    return {
        "ok":
            True,

        "reimbursement":
            _serialize_request(
                reimbursement
            ),
    }


@router.get(
    "/review-queue/{reimbursement_id}/audit",
)
def get_reimbursement_review_audit(
    reimbursement_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReimbursementRuntime = Depends(
        get_reimbursement_runtime
    ),
):

    context = (
        _require_reviewer_context(
            user=user,
            runtime=runtime,
        )
    )

    reimbursement = (
        _require_organization_request(
            runtime=runtime,

            organization_id=
                context.organization_id,

            reimbursement_id=
                reimbursement_id,
        )
    )

    if (
        reimbursement.user_id
        ==
        context.user_id
    ):

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "SELF_REVIEW_QUEUE_FORBIDDEN",
        )

    events = (
        runtime.audit
        .list_for_reimbursement(
            tenant_id=
                context.organization_id,

            reimbursement_id=
                reimbursement_id,
        )
    )

    return {
        "ok":
            True,

        "reimbursement_id":
            reimbursement_id,

        "count":
            len(events),

        "events": [
            {
                "event_id":
                    event.event_id,

                "action":
                    event.action,

                "actor_id":
                    event.actor_id,

                "details":
                    event.details,

                "created_at":
                    event.created_at
                    .isoformat(),
            }
            for event
            in events
        ],
    }


# SABINO_REIMBURSEMENT_PHASE_1B3C_QUEUE_END


# SABINO_REIMBURSEMENT_PHASE_2A2_RECEIPT_ROUTER_START

from .receipts.routes import (
    router as reimbursement_receipt_router,
)

router.include_router(
    reimbursement_receipt_router
)

# SABINO_REIMBURSEMENT_PHASE_2A2_RECEIPT_ROUTER_END


# SABINO_REIMBURSEMENT_PHASE_1B3D_ORG_ROUTER

from .corporate.admin_routes import (
    router as organization_admin_router,
)

router.include_router(
    organization_admin_router
)


@router.get(
    "/{reimbursement_id}",
)
def get_reimbursement(
    reimbursement_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReimbursementRuntime = Depends(
        get_reimbursement_runtime
    ),
):

    context = (
        _corporate_context_from_user(
            user=user,
            runtime=runtime,
        )
    )

    reimbursement = (
        _require_owned_request(
            runtime=runtime,

            organization_id=
                context.organization_id,

            user_id=
                context.user_id,

            reimbursement_id=
                reimbursement_id,
        )
    )

    return {
        "ok": True,

        "reimbursement":
            _serialize_request(
                reimbursement
            ),
    }


@router.post(
    "/{reimbursement_id}/submit",
)
def submit_reimbursement(
    reimbursement_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
        max_length=200,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReimbursementRuntime = Depends(
        get_reimbursement_runtime
    ),
):

    context = (
        _corporate_context_from_user(
            user=user,
            runtime=runtime,
        )
    )

    _require_owned_request(
        runtime=runtime,

        organization_id=
            context.organization_id,

        user_id=
            context.user_id,

        reimbursement_id=
            reimbursement_id,
    )

    try:

        reimbursement = (
            runtime.service.submit(
                tenant_id=
                    context.organization_id,

                reimbursement_id=
                    reimbursement_id,

                actor_id=
                    context.user_id,

                idempotency_key=
                    idempotency_key,
            )
        )

    except IdempotencyConflictError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,

            detail=
                str(exc),
        ) from exc

    except IdempotencyKeyError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,

            detail=
                str(exc),
        ) from exc

    except ValueError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,

            detail=str(exc),
        ) from exc

    return {
        "ok": True,

        "reimbursement":
            _serialize_request(
                reimbursement
            ),
    }


@router.post(
    "/{reimbursement_id}/analyze",
)
def analyze_reimbursement(
    reimbursement_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReimbursementRuntime = Depends(
        get_reimbursement_runtime
    ),
):

    context = (
        _corporate_context_from_user(
            user=user,
            runtime=runtime,
        )
    )

    _require_owned_request(
        runtime=runtime,

        organization_id=
            context.organization_id,

        user_id=
            context.user_id,

        reimbursement_id=
            reimbursement_id,
    )

    analysis = (
        runtime.service.analyze(
            tenant_id=
                context.organization_id,

            reimbursement_id=
                reimbursement_id,

            actor_id=
                "inna-reimbursement-agent",
        )
    )

    reimbursement = (
        _require_owned_request(
            runtime=runtime,

            organization_id=
                context.organization_id,

            user_id=
                context.user_id,

            reimbursement_id=
                reimbursement_id,
        )
    )

    return {
        "ok": True,

        "analysis":
            analysis.model_dump(
                mode="json"
            ),

        "reimbursement":
            _serialize_request(
                reimbursement
            ),
    }


@router.post(
    "/{reimbursement_id}/review",
)
def review_reimbursement(
    payload: ReimbursementReviewRequest,

    reimbursement_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
        max_length=200,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReimbursementRuntime = Depends(
        get_reimbursement_runtime
    ),
):

    context = (
        _corporate_context_from_user(
            user=user,
            runtime=runtime,
        )
    )

    if not can_review_reimbursements(
        context.member
    ):

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "REIMBURSEMENT_REVIEW_FORBIDDEN",
        )

    reimbursement = (
        _require_organization_request(
            runtime=runtime,

            organization_id=
                context.organization_id,

            reimbursement_id=
                reimbursement_id,
        )
    )

    if (
        reimbursement.user_id
        ==
        context.user_id
    ):

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "SELF_APPROVAL_FORBIDDEN",
        )

    try:

        result = (
            runtime.reviewer.review(
                tenant_id=
                    context.organization_id,

                reimbursement_id=
                    reimbursement_id,

                payload=HumanReviewInput(
                    reviewer_user_id=
                        context.user_id,

                    decision=
                        payload.decision,

                    reason=
                        payload.reason,
                ),

                idempotency_key=
                    idempotency_key,
            )
        )

    except IdempotencyConflictError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,

            detail=
                str(exc),
        ) from exc

    except IdempotencyKeyError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,

            detail=
                str(exc),
        ) from exc

    except ValueError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,

            detail=str(exc),
        ) from exc

    return {
        "ok": True,

        "reimbursement":
            _serialize_request(
                result
            ),
    }

# ============================================================
# SABINO_REIMBURSEMENT_PHASE_2B10C3_AUTO_APPROVAL_ADMIN_API
# ============================================================

from .auto_approval.routes import (
    router as reimbursement_auto_approval_router,
)

router.include_router(
    reimbursement_auto_approval_router
)


# SABINO_REIMBURSEMENT_PHASE_2B7B_POLICY_API

from .policy.routes import (
    router as reimbursement_policy_router,
)

router.include_router(
    reimbursement_policy_router
)


# ============================================================
# SABINO_REIMBURSEMENT_PHASE_2B8C_WORKFLOW_API
# ============================================================

from .corporate.rbac import (
    can_manage_reimbursement_payments,
)

from .idempotency import (
    IdempotencyConflictError,
    IdempotencyKeyError,
)

from .workflow import (
    ReimbursementTransitionError,
)

from .workflow_persistence import (
    persist_workflow_transition,
    workflow_persistence_capabilities,
)


class ReimbursementWorkflowActionRequest(
    BaseModel
):

    model_config = {
        "extra":
            "forbid"
    }

    reason: str | None = Field(
        default=None,
        max_length=500,
    )

    payment_reference: str | None = Field(
        default=None,
        max_length=200,
    )


def _workflow_details(
    payload:
        ReimbursementWorkflowActionRequest
        |
        None,
) -> dict:

    if payload is None:
        return {}

    details = {}

    if payload.reason:

        details[
            "reason"
        ] = payload.reason.strip()

    if payload.payment_reference:

        details[
            "payment_reference"
        ] = (
            payload.payment_reference
            .strip()
        )

    return details


def _workflow_response(
    reimbursement: ReimbursementRequest,
) -> dict:

    return {
        "ok":
            True,

        "reimbursement": {
            "id":
                reimbursement.id,

            "status":
                reimbursement.status.value,

            "requires_human_review":
                reimbursement
                .requires_human_review,
        },

        "organization_id_from_browser":
            False,

        "target_status_from_browser":
            False,

        "audit_action_from_browser":
            False,

        "automatic_approval":
            False,
    }



def _perform_workflow_transition(
    *,
    runtime: ReimbursementRuntime,
    organization_id: str,
    reimbursement_id: str,
    actor_id: str,
    target_status: ReimbursementStatus,
    details: dict | None = None,
    idempotency_key: str | None = None,
    idempotency_operation: str | None = None,
):

    try:

        return persist_workflow_transition(
            repository=
                runtime.repository,

            audit=
                runtime.audit,

            tenant_id=
                organization_id,

            reimbursement_id=
                reimbursement_id,

            actor_id=
                actor_id,

            target_status=
                target_status,

            details=
                details,

            idempotency_key=
                idempotency_key,

            idempotency_operation=
                idempotency_operation,

            idempotency_payload=
                (
                    details
                    if details is not None
                    else {}
                ),
        )

    except LookupError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "REIMBURSEMENT_NOT_FOUND",
        ) from exc

    except IdempotencyConflictError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,

            detail=
                str(exc),
        ) from exc

    except IdempotencyKeyError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,

            detail=
                str(exc),
        ) from exc

    except ReimbursementTransitionError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,

            detail=
                str(exc),
        ) from exc


@router.post(
    "/{reimbursement_id}/resubmit",
)
def resubmit_reimbursement(
    reimbursement_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    payload:
        ReimbursementWorkflowActionRequest
        |
        None = None,

    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
        max_length=200,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReimbursementRuntime = Depends(
        get_reimbursement_runtime
    ),
):

    context = (
        _corporate_context_from_user(
            user=user,
            runtime=runtime,
        )
    )

    _require_owned_request(
        runtime=runtime,

        organization_id=
            context.organization_id,

        user_id=
            context.user_id,

        reimbursement_id=
            reimbursement_id,
    )

    reimbursement = (
        _perform_workflow_transition(
            runtime=
                runtime,

            organization_id=
                context.organization_id,

            reimbursement_id=
                reimbursement_id,

            actor_id=
                context.user_id,

            target_status=
                ReimbursementStatus.SUBMITTED,

            details=
                _workflow_details(
                    payload
                ),

            idempotency_key=
                idempotency_key,

            idempotency_operation=
                "resubmit",
        )
    )

    return _workflow_response(
        reimbursement
    )


@router.post(
    "/{reimbursement_id}/cancel",
)
def cancel_reimbursement(
    reimbursement_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    payload:
        ReimbursementWorkflowActionRequest
        |
        None = None,

    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
        max_length=200,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReimbursementRuntime = Depends(
        get_reimbursement_runtime
    ),
):

    context = (
        _corporate_context_from_user(
            user=user,
            runtime=runtime,
        )
    )

    _require_owned_request(
        runtime=runtime,

        organization_id=
            context.organization_id,

        user_id=
            context.user_id,

        reimbursement_id=
            reimbursement_id,
    )

    reimbursement = (
        _perform_workflow_transition(
            runtime=
                runtime,

            organization_id=
                context.organization_id,

            reimbursement_id=
                reimbursement_id,

            actor_id=
                context.user_id,

            target_status=
                ReimbursementStatus.CANCELLED,

            details=
                _workflow_details(
                    payload
                ),

            idempotency_key=
                idempotency_key,

            idempotency_operation=
                "cancel",
        )
    )

    return _workflow_response(
        reimbursement
    )


def _require_payment_operator(
    *,
    context: CorporateContext,
) -> None:

    if not can_manage_reimbursement_payments(
        context.member
    ):

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "REIMBURSEMENT_PAYMENT_FORBIDDEN",
        )


def _require_not_own_payment(
    *,
    reimbursement: ReimbursementRequest,
    actor_user_id: str,
) -> None:

    if (
        reimbursement.user_id
        ==
        actor_user_id
    ):

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "REIMBURSEMENT_PAYMENT_SELF_ACTION_FORBIDDEN",
        )


@router.post(
    "/{reimbursement_id}/payment-pending",
)
def mark_reimbursement_payment_pending(
    reimbursement_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    payload:
        ReimbursementWorkflowActionRequest
        |
        None = None,

    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
        max_length=200,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReimbursementRuntime = Depends(
        get_reimbursement_runtime
    ),
):

    context = (
        _corporate_context_from_user(
            user=user,
            runtime=runtime,
        )
    )

    _require_payment_operator(
        context=context
    )

    existing = (
        _require_organization_request(
            runtime=runtime,

            organization_id=
                context.organization_id,

            reimbursement_id=
                reimbursement_id,
        )
    )

    _require_not_own_payment(
        reimbursement=
            existing,

        actor_user_id=
            context.user_id,
    )

    reimbursement = (
        _perform_workflow_transition(
            runtime=
                runtime,

            organization_id=
                context.organization_id,

            reimbursement_id=
                reimbursement_id,

            actor_id=
                context.user_id,

            target_status=
                ReimbursementStatus
                .PAYMENT_PENDING,

            details=
                _workflow_details(
                    payload
                ),

            idempotency_key=
                idempotency_key,

            idempotency_operation=
                "payment_pending",
        )
    )

    return _workflow_response(
        reimbursement
    )


@router.post(
    "/{reimbursement_id}/paid",
)
def mark_reimbursement_paid(
    reimbursement_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    payload:
        ReimbursementWorkflowActionRequest
        |
        None = None,

    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
        max_length=200,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReimbursementRuntime = Depends(
        get_reimbursement_runtime
    ),
):

    context = (
        _corporate_context_from_user(
            user=user,
            runtime=runtime,
        )
    )

    _require_payment_operator(
        context=context
    )

    existing = (
        _require_organization_request(
            runtime=runtime,

            organization_id=
                context.organization_id,

            reimbursement_id=
                reimbursement_id,
        )
    )

    _require_not_own_payment(
        reimbursement=
            existing,

        actor_user_id=
            context.user_id,
    )

    reimbursement = (
        _perform_workflow_transition(
            runtime=
                runtime,

            organization_id=
                context.organization_id,

            reimbursement_id=
                reimbursement_id,

            actor_id=
                context.user_id,

            target_status=
                ReimbursementStatus.PAID,

            details=
                _workflow_details(
                    payload
                ),

            idempotency_key=
                idempotency_key,

            idempotency_operation=
                "paid",
        )
    )

    return _workflow_response(
        reimbursement
    )


@router.get(
    "/workflow/capabilities",
)
def reimbursement_workflow_capabilities(
    user: dict = Depends(
        get_financeiro_entitled_user
    ),
):

    capabilities = (
        workflow_persistence_capabilities()
    )

    return {
        **capabilities,

        "api_version":
            "reimbursement-2b8c",

        "resubmit_endpoint":
            True,

        "cancel_endpoint":
            True,

        "payment_pending_endpoint":
            True,

        "paid_endpoint":
            True,

        "payment_roles": [
            "finance_approver",
            "organization_admin",
        ],

        "self_payment_forbidden":
            True,

        "organization_id_from_browser":
            False,

        "target_status_from_browser":
            False,

        "audit_action_from_browser":
            False,
    }


# SABINO_REIMBURSEMENT_PHASE_2B8C_WORKFLOW_API_END

