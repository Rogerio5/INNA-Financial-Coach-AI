from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .models import (
    OrganizationMember,
    OrganizationRole,
)

from .repository import (
    CorporateRepository,
)


def _utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


class InMemoryCorporateRepository(
    CorporateRepository
):

    def __init__(self) -> None:

        self.organizations: dict[
            str,
            dict,
        ] = {}

        self.members: dict[
            tuple[str, str],
            OrganizationMember,
        ] = {}

    def create_organization(
        self,
        *,
        name: str,
        created_by_user_id: str,
    ) -> dict:

        organization_id = (
            "org_"
            + uuid4().hex
        )

        now = _utc_now()

        organization = {
            "organization_id":
                organization_id,

            "name":
                name,

            "created_by_user_id":
                created_by_user_id,

            "active":
                True,

            "created_at":
                now,

            "updated_at":
                now,
        }

        self.organizations[
            organization_id
        ] = organization

        self.add_member(
            organization_id=
                organization_id,

            user_id=
                created_by_user_id,

            role=(
                OrganizationRole
                .ORGANIZATION_ADMIN
            ),
        )

        return organization

    def get_organization(
        self,
        *,
        organization_id: str,
    ) -> dict | None:

        return self.organizations.get(
            organization_id
        )

    def add_member(
        self,
        *,
        organization_id: str,
        user_id: str,
        role: OrganizationRole,
    ) -> OrganizationMember:

        now = _utc_now()

        key = (
            organization_id,
            user_id,
        )

        existing = self.members.get(
            key
        )

        member = OrganizationMember(
            organization_id=
                organization_id,

            user_id=
                user_id,

            role=
                role,

            active=
                True,

            created_at=(
                existing.created_at
                if existing
                else now
            ),

            updated_at=
                now,
        )

        self.members[
            key
        ] = member

        return member

    def get_member(
        self,
        *,
        organization_id: str,
        user_id: str,
    ) -> OrganizationMember | None:

        return self.members.get(
            (
                organization_id,
                user_id,
            )
        )

    def list_user_memberships(
        self,
        *,
        user_id: str,
    ) -> list[OrganizationMember]:

        return [
            member
            for member
            in self.members.values()
            if (
                member.user_id
                ==
                user_id

                and

                member.active
            )
        ]

    def list_organization_members(
        self,
        *,
        organization_id: str,
        include_inactive: bool = False,
    ) -> list[OrganizationMember]:

        items = [
            member
            for member
            in self.members.values()
            if (
                member.organization_id
                ==
                organization_id
            )
        ]

        if not include_inactive:

            items = [
                member
                for member
                in items
                if member.active
            ]

        return sorted(
            items,
            key=lambda member:
                member.created_at,
        )

    def deactivate_member(
        self,
        *,
        organization_id: str,
        user_id: str,
    ) -> bool:

        key = (
            organization_id,
            user_id,
        )

        member = self.members.get(
            key
        )

        if member is None:
            return False

        now = _utc_now()

        self.members[key] = (
            OrganizationMember(
                organization_id=
                    member.organization_id,

                user_id=
                    member.user_id,

                role=
                    member.role,

                active=
                    False,

                created_at=
                    member.created_at,

                updated_at=
                    now,
            )
        )

        return True