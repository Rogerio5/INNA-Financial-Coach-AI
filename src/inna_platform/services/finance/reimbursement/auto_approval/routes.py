from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from src.inna_platform.services.finance.finance_access_gate import (
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
    AutoApprovalConfiguration,
)

from .repository import (
    AutoApprovalConfigurationRepository,
    PostgresAutoApprovalConfigurationRepository,
)

from .schemas import (
    AutoApprovalConfigurationUpdateRequest,
)

from .service import (
    AutoApprovalConfigurationService,
)


from .execution_control import (
    auto_approval_execution_capabilities,
)


router = APIRouter(
    prefix="/organization/auto-approval",
    tags=[
        "Finance Reimbursement Auto Approval"
    ],
)


@dataclass
class AutoApprovalApiRuntime:
    corporate_repository: CorporateRepository

    config_repository: AutoApprovalConfigurationRepository

    audit: CorporateAuditService | PostgresCorporateAuditService

    service: AutoApprovalConfigurationService



@lru_cache(maxsize=1)
def get_auto_approval_api_runtime(
) -> AutoApprovalApiRuntime:

    config_repository = (
        PostgresAutoApprovalConfigurationRepository()
    )

    audit = (
        PostgresCorporateAuditService()
    )

    return AutoApprovalApiRuntime(
        corporate_repository=
            PostgresCorporateRepository(),

        config_repository=
            config_repository,

        audit=
            audit,

        service=
            AutoApprovalConfigurationService(
                repository=
                    config_repository,

                audit=
                    audit,
            ),
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
    runtime: AutoApprovalApiRuntime,
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


def _serialize_config(
    config:
        AutoApprovalConfiguration
        |
        None,
) -> dict:

    if config is None:

        return {
            "configured":
                False,

            "enabled":
                False,

            "amount_limit_minor":
                None,

            "version":
                None,

            "updated_by_user_id":
                None,

            "created_at":
                None,

            "updated_at":
                None,
        }


    return {
        "configured":
            True,

        "enabled":
            config.enabled,

        "amount_limit_minor":
            config.amount_limit_minor,

        "version":
            config.version,

        "updated_by_user_id":
            config.updated_by_user_id,

        "created_at":
            config.created_at.isoformat(),

        "updated_at":
            config.updated_at.isoformat(),
    }


@router.get("")
def get_auto_approval_configuration(
    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime:
        AutoApprovalApiRuntime
        =
        Depends(
            get_auto_approval_api_runtime
        ),
):

    context = (
        _require_organization_admin(
            user=user,
            runtime=runtime,
        )
    )

    config = (
        runtime.config_repository.get(
            organization_id=
                context.organization_id
        )
    )

    return {
        "ok":
            True,

        "organization_id_from_browser":
            False,

        "configuration":
            _serialize_config(
                config
            ),

        "default_disabled":
            True,

        "automatic_approval":
            False,

        "automatic_payment":
            False,

        "human_review_required":
            True,

        "global_execution":
            auto_approval_execution_capabilities(),
    }


@router.put("")
def update_auto_approval_configuration(
    payload:
        AutoApprovalConfigurationUpdateRequest,

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime:
        AutoApprovalApiRuntime
        =
        Depends(
            get_auto_approval_api_runtime
        ),
):

    context = (
        _require_organization_admin(
            user=user,
            runtime=runtime,
        )
    )


    try:

        config = (
            runtime.service.configure(
                organization_id=
                    context.organization_id,

                actor_user_id=
                    context.user_id,

                enabled=
                    payload.enabled,

                amount_limit_minor=
                    payload.amount_limit_minor,

                expected_version=
                    payload.expected_version,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_422_UNPROCESSABLE_CONTENT,

            detail=
                str(exc),
        ) from exc


    return {
        "ok":
            True,

        "organization_id_from_browser":
            False,

        "configuration":
            _serialize_config(
                config
            ),

        "automatic_approval":
            False,

        "auto_transition_to_approved":
            False,

        "automatic_payment":
            False,

        "human_review_required":
            True,

        "global_execution":
            auto_approval_execution_capabilities(),
    }