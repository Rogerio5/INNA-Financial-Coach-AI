from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from ...finance_access_gate import (
    get_financeiro_entitled_user,
)

from ..corporate.audit import (
    CorporateAuditService,
    PostgresCorporateAuditService,
)

from ..corporate.context import (
    CorporateContext,
    resolve_corporate_context,
)

from ..corporate.models import (
    OrganizationRole,
)

from ..corporate.repository import (
    CorporateRepository,
    PostgresCorporateRepository,
)

from .models import (
    ReimbursementPolicy,
)

from .persistence import (
    persist_new_policy_version,
)

from .repository import (
    PostgresReimbursementPolicyRepository,
    ReimbursementPolicyRepository,
)

from .schemas import (
    ReimbursementPolicyCreateRequest,
)


router = APIRouter(
    prefix="/organization/policy",
    tags=[
        "Finance Reimbursement Policy"
    ],
)


@dataclass
class PolicyApiRuntime:

    corporate_repository: CorporateRepository

    policy_repository: ReimbursementPolicyRepository

    audit: (
        CorporateAuditService
        |
        PostgresCorporateAuditService
    )


@lru_cache(maxsize=1)
def get_policy_api_runtime(
) -> PolicyApiRuntime:

    return PolicyApiRuntime(
        corporate_repository=
            PostgresCorporateRepository(),

        policy_repository=
            PostgresReimbursementPolicyRepository(),

        audit=
            PostgresCorporateAuditService(),
    )


def _user_id(
    user: dict,
) -> str:

    value = str(
        user.get(
            "user_id",
            "",
        )
    ).strip()

    if not value:

        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,

            detail=
                "INVALID_AUTHENTICATED_IDENTITY",
        )

    return value


def _require_organization_admin(
    *,
    user: dict,
    runtime: PolicyApiRuntime,
) -> CorporateContext:

    user_id = _user_id(
        user
    )

    try:

        context = (
            resolve_corporate_context(
                repository=
                    runtime.corporate_repository,

                user_id=
                    user_id,
            )
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

                detail=
                    "MULTIPLE_ORGANIZATIONS_REQUIRE_SELECTION",
            ) from exc

        raise

    if context is None:

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "ORGANIZATION_MEMBERSHIP_REQUIRED",
        )

    if (
        not context.member.active
        or
        context.member.role
        !=
        OrganizationRole.ORGANIZATION_ADMIN
    ):

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "ORGANIZATION_ADMIN_REQUIRED",
        )

    return context


def _serialize_policy(
    policy: ReimbursementPolicy,
) -> dict:

    return {
        "policy_id":
            policy.policy_id,

        "version":
            policy.version,

        "allowed_categories":
            list(
                policy.allowed_categories
            ),

        "amount_limit_minor":
            policy.amount_limit_minor,

        "category_limits_minor":
            dict(
                policy.category_limits_minor
            ),

        "receipt_required":
            policy.receipt_required,

        "submission_deadline_days":
            policy.submission_deadline_days,

        "allowed_currencies":
            list(
                policy.allowed_currencies
            ),

        "active":
            policy.active,

        "created_at":
            policy.created_at.isoformat(),

        "updated_at":
            policy.updated_at.isoformat(),
    }


@router.get("")
def get_active_reimbursement_policy(
    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: PolicyApiRuntime = Depends(
        get_policy_api_runtime
    ),
):

    context = (
        _require_organization_admin(
            user=user,
            runtime=runtime,
        )
    )

    policy = (
        runtime.policy_repository.get_active(
            organization_id=
                context.organization_id,
        )
    )

    return {
        "ok":
            True,

        "configured":
            policy is not None,

        "policy":
            (
                _serialize_policy(
                    policy
                )
                if policy is not None
                else None
            ),

        "organization_id_from_browser":
            False,

        "human_review_required":
            True,

        "automatic_approval":
            False,
    }


@router.get(
    "/versions"
)
def list_reimbursement_policy_versions(
    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: PolicyApiRuntime = Depends(
        get_policy_api_runtime
    ),
):

    context = (
        _require_organization_admin(
            user=user,
            runtime=runtime,
        )
    )

    versions = (
        runtime.policy_repository.list_versions(
            organization_id=
                context.organization_id,
        )
    )

    return {
        "ok":
            True,

        "policies": [
            _serialize_policy(
                policy
            )
            for policy
            in versions
        ],

        "organization_id_from_browser":
            False,
    }


@router.post(
    "",
    status_code=
        status.HTTP_201_CREATED,
)
def create_reimbursement_policy_version(
    payload:
        ReimbursementPolicyCreateRequest,

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: PolicyApiRuntime = Depends(
        get_policy_api_runtime
    ),
):

    context = (
        _require_organization_admin(
            user=user,
            runtime=runtime,
        )
    )

    try:

        policy = (
            persist_new_policy_version(
                policy_repository=
                    runtime.policy_repository,

                audit=
                    runtime.audit,

                organization_id=
                    context.organization_id,

                actor_user_id=
                    context.user_id,

                allowed_categories=
                    payload.allowed_categories,

                amount_limit_minor=
                    payload.amount_limit_minor,

                category_limits_minor=
                    payload.category_limits_minor,

                receipt_required=
                    payload.receipt_required,

                submission_deadline_days=
                    payload.submission_deadline_days,

                allowed_currencies=
                    payload.allowed_currencies,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_422_UNPROCESSABLE_ENTITY,

            detail=
                str(exc),
        ) from exc

    except LookupError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                str(exc),
        ) from exc

    return {
        "ok":
            True,

        "policy":
            _serialize_policy(
                policy
            ),

        "organization_id_from_browser":
            False,

        "policy_version_from_browser":
            False,

        "policy_id_from_browser":
            False,

        "human_review_required":
            True,

        "automatic_approval":
            False,
    }
