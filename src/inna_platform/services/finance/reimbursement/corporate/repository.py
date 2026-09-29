from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import uuid4

from src.database.connection import cursor_postgres

from .db_schema import (
    ORGANIZATION_MEMBER_TABLE,
    ORGANIZATION_TABLE,
    ensure_corporate_schema,
)

from .models import (
    OrganizationMember,
    OrganizationRole,
)


class CorporateRepository(ABC):

    @abstractmethod
    def create_organization(
        self,
        *,
        name: str,
        created_by_user_id: str,
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_organization(
        self,
        *,
        organization_id: str,
    ) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def add_member(
        self,
        *,
        organization_id: str,
        user_id: str,
        role: OrganizationRole,
    ) -> OrganizationMember:
        raise NotImplementedError

    @abstractmethod
    def get_member(
        self,
        *,
        organization_id: str,
        user_id: str,
    ) -> OrganizationMember | None:
        raise NotImplementedError

    @abstractmethod
    def list_user_memberships(
        self,
        *,
        user_id: str,
    ) -> list[OrganizationMember]:
        raise NotImplementedError

    @abstractmethod
    def list_organization_members(
        self,
        *,
        organization_id: str,
        include_inactive: bool = False,
    ) -> list[OrganizationMember]:
        raise NotImplementedError

    @abstractmethod
    def deactivate_member(
        self,
        *,
        organization_id: str,
        user_id: str,
    ) -> bool:
        raise NotImplementedError


def _member_from_row(
    row: dict[str, Any],
) -> OrganizationMember:

    return OrganizationMember(
        organization_id=str(
            row["organization_id"]
        ),

        user_id=str(
            row["user_id"]
        ),

        role=OrganizationRole(
            row["role"]
        ),

        active=bool(
            row["active"]
        ),

        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class PostgresCorporateRepository(
    CorporateRepository
):

    def __init__(self) -> None:
        ensure_corporate_schema()

    def create_organization(
        self,
        *,
        name: str,
        created_by_user_id: str,
    ) -> dict:

        normalized_name = str(
            name or ""
        ).strip()

        user_id = str(
            created_by_user_id or ""
        ).strip()

        if not normalized_name:
            raise ValueError(
                "ORGANIZATION_NAME_REQUIRED"
            )

        if not user_id:
            raise ValueError(
                "CREATED_BY_USER_REQUIRED"
            )

        organization_id = (
            "org_"
            + uuid4().hex
        )

        sql = f"""
        INSERT INTO {ORGANIZATION_TABLE} (
            organization_id,
            name,
            created_by_user_id
        )
        VALUES (
            %s,
            %s,
            %s
        )
        RETURNING
            organization_id,
            name,
            created_by_user_id,
            active,
            created_at,
            updated_at
        """

        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    organization_id,
                    normalized_name,
                    user_id,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "ORGANIZATION_CREATE_FAILED"
            )

        organization = dict(row)

        self.add_member(
            organization_id=
                organization_id,

            user_id=
                user_id,

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

        sql = f"""
        SELECT
            organization_id,
            name,
            created_by_user_id,
            active,
            created_at,
            updated_at

        FROM {ORGANIZATION_TABLE}

        WHERE
            organization_id = %s

        LIMIT 1
        """

        with cursor_postgres(
            dict_cursor=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    str(
                        organization_id
                    ).strip(),
                ),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def add_member(
        self,
        *,
        organization_id: str,
        user_id: str,
        role: OrganizationRole,
    ) -> OrganizationMember:

        organization_id = str(
            organization_id or ""
        ).strip()

        user_id = str(
            user_id or ""
        ).strip()

        if not organization_id:
            raise ValueError(
                "ORGANIZATION_ID_REQUIRED"
            )

        if not user_id:
            raise ValueError(
                "USER_ID_REQUIRED"
            )

        sql = f"""
        INSERT INTO {ORGANIZATION_MEMBER_TABLE} (
            organization_id,
            user_id,
            role,
            active
        )
        VALUES (
            %s,
            %s,
            %s,
            TRUE
        )

        ON CONFLICT (
            organization_id,
            user_id
        )
        DO UPDATE SET
            role =
                EXCLUDED.role,

            active =
                TRUE,

            updated_at =
                NOW()

        RETURNING
            organization_id,
            user_id,
            role,
            active,
            created_at,
            updated_at
        """

        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    organization_id,
                    user_id,
                    role.value,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "ORGANIZATION_MEMBER_SAVE_FAILED"
            )

        return _member_from_row(
            dict(row)
        )

    def get_member(
        self,
        *,
        organization_id: str,
        user_id: str,
    ) -> OrganizationMember | None:

        sql = f"""
        SELECT
            organization_id,
            user_id,
            role,
            active,
            created_at,
            updated_at

        FROM {ORGANIZATION_MEMBER_TABLE}

        WHERE
            organization_id = %s
            AND
            user_id = %s

        LIMIT 1
        """

        with cursor_postgres(
            dict_cursor=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    organization_id,
                    user_id,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return _member_from_row(
            dict(row)
        )

    def list_user_memberships(
        self,
        *,
        user_id: str,
    ) -> list[OrganizationMember]:

        sql = f"""
        SELECT
            organization_id,
            user_id,
            role,
            active,
            created_at,
            updated_at

        FROM {ORGANIZATION_MEMBER_TABLE}

        WHERE
            user_id = %s
            AND
            active = TRUE

        ORDER BY
            created_at ASC
        """

        with cursor_postgres(
            dict_cursor=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    user_id,
                ),
            )

            rows = cursor.fetchall()

        return [
            _member_from_row(
                dict(row)
            )
            for row
            in rows
        ]

    def list_organization_members(
        self,
        *,
        organization_id: str,
        include_inactive: bool = False,
    ) -> list[OrganizationMember]:

        if include_inactive:

            sql = f"""
            SELECT
                organization_id,
                user_id,
                role,
                active,
                created_at,
                updated_at

            FROM {ORGANIZATION_MEMBER_TABLE}

            WHERE
                organization_id = %s

            ORDER BY
                created_at ASC
            """

        else:

            sql = f"""
            SELECT
                organization_id,
                user_id,
                role,
                active,
                created_at,
                updated_at

            FROM {ORGANIZATION_MEMBER_TABLE}

            WHERE
                organization_id = %s
                AND active = TRUE

            ORDER BY
                created_at ASC
            """

        with cursor_postgres(
            dict_cursor=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    organization_id,
                ),
            )

            rows = cursor.fetchall()

        return [
            _member_from_row(
                dict(row)
            )
            for row
            in rows
        ]

    def deactivate_member(
        self,
        *,
        organization_id: str,
        user_id: str,
    ) -> bool:

        sql = f"""
        UPDATE {ORGANIZATION_MEMBER_TABLE}

        SET
            active = FALSE,
            updated_at = NOW()

        WHERE
            organization_id = %s
            AND
            user_id = %s

        RETURNING user_id
        """

        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    organization_id,
                    user_id,
                ),
            )

            row = cursor.fetchone()

        return row is not None