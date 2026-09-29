from __future__ import annotations

from dataclasses import dataclass

from .models import OrganizationMember
from .repository import CorporateRepository


@dataclass(frozen=True)
class CorporateContext:
    organization_id: str
    user_id: str
    member: OrganizationMember


def resolve_corporate_context(
    *,
    repository: CorporateRepository,
    user_id: str,
) -> CorporateContext | None:

    normalized_user_id = str(
        user_id or ""
    ).strip()

    if not normalized_user_id:
        return None

    memberships = repository.list_user_memberships(
        user_id=normalized_user_id
    )

    active_memberships = [
        member
        for member in memberships
        if member.active
    ]

    if not active_memberships:
        return None

    if len(active_memberships) > 1:
        raise ValueError(
            "MULTIPLE_ORGANIZATIONS_REQUIRE_SELECTION"
        )

    member = active_memberships[0]

    return CorporateContext(
        organization_id=member.organization_id,
        user_id=normalized_user_id,
        member=member,
    )