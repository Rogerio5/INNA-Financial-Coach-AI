from __future__ import annotations

from functools import lru_cache

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
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

from .audit import (
    CorporateAuditService,
    PostgresCorporateAuditService,
)

from .context import (
    CorporateContext,
    resolve_corporate_context,
)

from .identity_directory import (
    IdentityDirectory,
    PostgresIdentityDirectory,
)

from .models import (
    OrganizationMember,
    OrganizationRole,
)

from .rbac import (
    can_manage_members,
)

from .repository import (
    CorporateRepository,
    PostgresCorporateRepository,
)


router = APIRouter(
    prefix="/organization",
    tags=[
        "Finance Reimbursement Organization"
    ],
)


class OrganizationMemberCreateRequest(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid",
    )

    email: str = Field(
        min_length=3,
        max_length=320,
    )

    role: OrganizationRole


class OrganizationMemberRoleRequest(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid",
    )

    role: OrganizationRole


@lru_cache(maxsize=1)
def get_corporate_repository(
) -> CorporateRepository:

    return (
        PostgresCorporateRepository()
    )


@lru_cache(maxsize=1)
def get_identity_directory(
) -> IdentityDirectory:

    return (
        PostgresIdentityDirectory()
    )


@lru_cache(maxsize=1)
def get_corporate_audit_service(
) -> CorporateAuditService:

    return (
        PostgresCorporateAuditService()
    )


def _authenticated_user_id(
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


def _admin_context(
    *,
    user: dict,
    repository: CorporateRepository,
) -> CorporateContext:

    user_id = (
        _authenticated_user_id(
            user
        )
    )

    try:

        context = (
            resolve_corporate_context(
                repository=
                    repository,

                user_id=
                    user_id,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,

            detail=str(exc),
        ) from exc

    if context is None:

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "ORGANIZATION_MEMBERSHIP_REQUIRED",
        )

    if not can_manage_members(
        context.member
    ):

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "ORGANIZATION_ADMIN_REQUIRED",
        )

    return context


def _serialize_member(
    *,
    member: OrganizationMember,
    identity: IdentityDirectory,
) -> dict:

    user = identity.get_user_by_id(
        user_id=member.user_id
    )

    return {
        "user_id":
            member.user_id,

        "email": (
            user.get(
                "email"
            )
            if user
            else None
        ),

        "role":
            member.role.value,

        "active":
            member.active,

        "created_at":
            member.created_at
            .isoformat(),

        "updated_at":
            member.updated_at
            .isoformat(),
    }


@router.get(
    "",
)
def get_organization_admin(
    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    repository: CorporateRepository = Depends(
        get_corporate_repository
    ),
):

    context = _admin_context(
        user=user,
        repository=repository,
    )

    organization = (
        repository.get_organization(
            organization_id=
                context.organization_id
        )
    )

    if organization is None:

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "ORGANIZATION_NOT_FOUND",
        )

    return {
        "ok":
            True,

        "organization": {
            "organization_id":
                organization[
                    "organization_id"
                ],

            "name":
                organization[
                    "name"
                ],

            "active":
                bool(
                    organization[
                        "active"
                    ]
                ),

            "created_at":
                organization[
                    "created_at"
                ].isoformat(),

            "updated_at":
                organization[
                    "updated_at"
                ].isoformat(),
        },

        "current_role":
            context.member.role.value,
    }


@router.get(
    "/members",
)
def list_organization_members(
    include_inactive: bool = Query(
        default=False,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    repository: CorporateRepository = Depends(
        get_corporate_repository
    ),

    identity: IdentityDirectory = Depends(
        get_identity_directory
    ),
):

    context = _admin_context(
        user=user,
        repository=repository,
    )

    members = (
        repository
        .list_organization_members(
            organization_id=
                context.organization_id,

            include_inactive=
                include_inactive,
        )
    )

    return {
        "ok":
            True,

        "count":
            len(members),

        "members": [
            _serialize_member(
                member=member,
                identity=identity,
            )
            for member
            in members
        ],
    }


@router.post(
    "/members",
    status_code=
        status.HTTP_201_CREATED,
)
def add_organization_member(
    payload:
        OrganizationMemberCreateRequest,

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    repository: CorporateRepository = Depends(
        get_corporate_repository
    ),

    identity: IdentityDirectory = Depends(
        get_identity_directory
    ),

    audit: CorporateAuditService = Depends(
        get_corporate_audit_service
    ),
):

    context = _admin_context(
        user=user,
        repository=repository,
    )

    target_user = (
        identity.get_user_by_email(
            email=
                payload.email
        )
    )

    if target_user is None:

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "AUTH_USER_NOT_FOUND",
        )

    target_user_id = str(
        target_user[
            "user_id"
        ]
    )

    existing = (
        repository.get_member(
            organization_id=
                context.organization_id,

            user_id=
                target_user_id,
        )
    )

    if (
        existing is not None
        and
        existing.active
    ):

        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,

            detail=
                "ORGANIZATION_MEMBER_ALREADY_EXISTS",
        )

    member = repository.add_member(
        organization_id=
            context.organization_id,

        user_id=
            target_user_id,

        role=
            payload.role,
    )

    audit.record(
        organization_id=
            context.organization_id,

        action=
            "organization.member.added",

        actor_user_id=
            context.user_id,

        target_user_id=
            target_user_id,

        details={
            "role":
                payload.role.value,

            "email":
                target_user[
                    "email"
                ],
        },
    )

    return {
        "ok":
            True,

        "member":
            _serialize_member(
                member=member,
                identity=identity,
            ),
    }


@router.patch(
    "/members/{target_user_id}/role",
)
def change_organization_member_role(
    payload:
        OrganizationMemberRoleRequest,

    target_user_id: str = Path(
        min_length=1,
        max_length=200,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    repository: CorporateRepository = Depends(
        get_corporate_repository
    ),

    identity: IdentityDirectory = Depends(
        get_identity_directory
    ),

    audit: CorporateAuditService = Depends(
        get_corporate_audit_service
    ),
):

    context = _admin_context(
        user=user,
        repository=repository,
    )

    if (
        target_user_id
        ==
        context.user_id
    ):

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "SELF_ROLE_CHANGE_FORBIDDEN",
        )

    existing = repository.get_member(
        organization_id=
            context.organization_id,

        user_id=
            target_user_id,
    )

    if (
        existing is None
        or
        not existing.active
    ):

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "ORGANIZATION_MEMBER_NOT_FOUND",
        )

    previous_role = (
        existing.role.value
    )

    member = repository.add_member(
        organization_id=
            context.organization_id,

        user_id=
            target_user_id,

        role=
            payload.role,
    )

    audit.record(
        organization_id=
            context.organization_id,

        action=
            "organization.member.role_changed",

        actor_user_id=
            context.user_id,

        target_user_id=
            target_user_id,

        details={
            "previous_role":
                previous_role,

            "new_role":
                payload.role.value,
        },
    )

    return {
        "ok":
            True,

        "member":
            _serialize_member(
                member=member,
                identity=identity,
            ),
    }


@router.delete(
    "/members/{target_user_id}",
)
def deactivate_organization_member(
    target_user_id: str = Path(
        min_length=1,
        max_length=200,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    repository: CorporateRepository = Depends(
        get_corporate_repository
    ),

    audit: CorporateAuditService = Depends(
        get_corporate_audit_service
    ),
):

    context = _admin_context(
        user=user,
        repository=repository,
    )

    if (
        target_user_id
        ==
        context.user_id
    ):

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "SELF_DEACTIVATION_FORBIDDEN",
        )

    existing = repository.get_member(
        organization_id=
            context.organization_id,

        user_id=
            target_user_id,
    )

    if (
        existing is None
        or
        not existing.active
    ):

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "ORGANIZATION_MEMBER_NOT_FOUND",
        )

    deactivated = (
        repository.deactivate_member(
            organization_id=
                context.organization_id,

            user_id=
                target_user_id,
        )
    )

    if not deactivated:

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "ORGANIZATION_MEMBER_NOT_FOUND",
        )

    audit.record(
        organization_id=
            context.organization_id,

        action=
            "organization.member.deactivated",

        actor_user_id=
            context.user_id,

        target_user_id=
            target_user_id,

        details={
            "previous_role":
                existing.role.value,
        },
    )

    return {
        "ok":
            True,

        "deactivated_user_id":
            target_user_id,
    }


@router.get(
    "/audit",
)
def list_organization_audit(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    repository: CorporateRepository = Depends(
        get_corporate_repository
    ),

    audit: CorporateAuditService = Depends(
        get_corporate_audit_service
    ),
):

    context = _admin_context(
        user=user,
        repository=repository,
    )

    events = audit.list_events(
        organization_id=
            context.organization_id,

        limit=
            limit,
    )

    return {
        "ok":
            True,

        "count":
            len(events),

        "events": [
            {
                "event_id":
                    event.event_id,

                "action":
                    event.action,

                "actor_user_id":
                    event.actor_user_id,

                "target_user_id":
                    event.target_user_id,

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