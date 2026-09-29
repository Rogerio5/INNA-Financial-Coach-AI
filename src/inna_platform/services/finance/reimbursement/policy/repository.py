from __future__ import annotations

import json

from abc import ABC, abstractmethod

from src.database.connection import (
    conexao_postgres,
    cursor_postgres,
)

from .db_schema import (
    POLICY_TABLE,
    ensure_policy_schema,
)

from .models import (
    ReimbursementPolicy,
)


def _from_row(
    row: dict,
) -> ReimbursementPolicy:

    categories = row.get(
        "allowed_categories"
    )

    category_limits = row.get(
        "category_limits_minor"
    )

    currencies = row.get(
        "allowed_currencies"
    )

    if isinstance(
        categories,
        str,
    ):
        categories = json.loads(
            categories
        )

    if isinstance(
        category_limits,
        str,
    ):
        category_limits = json.loads(
            category_limits
        )

    if isinstance(
        currencies,
        str,
    ):
        currencies = json.loads(
            currencies
        )

    return ReimbursementPolicy(
        policy_id=
            str(
                row["policy_id"]
            ),

        organization_id=
            str(
                row["organization_id"]
            ),

        version=
            int(
                row["version"]
            ),

        allowed_categories=
            list(
                categories or []
            ),

        amount_limit_minor=
            (
                int(
                    row["amount_limit_minor"]
                )
                if row.get(
                    "amount_limit_minor"
                )
                is not None
                else None
            ),

        category_limits_minor={
            str(key):
                int(value)

            for key, value in (
                category_limits
                or
                {}
            ).items()
        },

        receipt_required=
            bool(
                row["receipt_required"]
            ),

        submission_deadline_days=
            (
                int(
                    row[
                        "submission_deadline_days"
                    ]
                )
                if row.get(
                    "submission_deadline_days"
                )
                is not None
                else None
            ),

        allowed_currencies=
            list(
                currencies or []
            ),

        active=
            bool(
                row["active"]
            ),

        created_at=
            row["created_at"],

        updated_at=
            row["updated_at"],
    )


class ReimbursementPolicyRepository(
    ABC
):

    @abstractmethod
    def save(
        self,
        policy: ReimbursementPolicy,
    ) -> ReimbursementPolicy:
        raise NotImplementedError

    @abstractmethod
    def get_active(
        self,
        *,
        organization_id: str,
    ) -> ReimbursementPolicy | None:
        raise NotImplementedError

    @abstractmethod
    def list_versions(
        self,
        *,
        organization_id: str,
    ) -> list[ReimbursementPolicy]:
        raise NotImplementedError


class InMemoryReimbursementPolicyRepository(
    ReimbursementPolicyRepository
):

    def __init__(self) -> None:
        self._items: dict[
            str,
            list[ReimbursementPolicy]
        ] = {}

    def save(
        self,
        policy: ReimbursementPolicy,
    ) -> ReimbursementPolicy:

        versions = self._items.setdefault(
            policy.organization_id,
            [],
        )

        for existing in versions:

            if (
                existing.version
                ==
                policy.version
            ):
                raise ValueError(
                    "POLICY_VERSION_ALREADY_EXISTS"
                )

        if policy.active:

            for existing in versions:
                existing.active = False

        versions.append(
            policy
        )

        return policy

    def get_active(
        self,
        *,
        organization_id: str,
    ) -> ReimbursementPolicy | None:

        versions = self._items.get(
            organization_id,
            [],
        )

        active = [
            item
            for item in versions
            if item.active
        ]

        if not active:
            return None

        return sorted(
            active,
            key=lambda item:
                item.version,
            reverse=True,
        )[0]

    def list_versions(
        self,
        *,
        organization_id: str,
    ) -> list[ReimbursementPolicy]:

        return sorted(
            list(
                self._items.get(
                    organization_id,
                    [],
                )
            ),
            key=lambda item:
                item.version,
            reverse=True,
        )


class PostgresReimbursementPolicyRepository(
    ReimbursementPolicyRepository
):

    def __init__(self) -> None:
        ensure_policy_schema()

    def save(
        self,
        policy: ReimbursementPolicy,
    ) -> ReimbursementPolicy:

        insert_sql = f"""
        INSERT INTO {POLICY_TABLE} (
            policy_id,
            organization_id,
            version,
            allowed_categories,
            amount_limit_minor,
            category_limits_minor,
            receipt_required,
            submission_deadline_days,
            allowed_currencies,
            active,
            created_at,
            updated_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s::jsonb,
            %s,
            %s::jsonb,
            %s,
            %s,
            %s::jsonb,
            %s,
            %s,
            %s
        )
        """

        deactivate_sql = f"""
        UPDATE {POLICY_TABLE}

        SET
            active = FALSE,
            updated_at = NOW()

        WHERE
            organization_id = %s
            AND
            active = TRUE
        """

        with conexao_postgres(
            autocommit=False,
            commit_automatico=True,
        ) as connection:

            cursor = connection.cursor()

            try:

                if policy.active:

                    cursor.execute(
                        deactivate_sql,
                        (
                            policy.organization_id,
                        ),
                    )

                cursor.execute(
                    insert_sql,
                    (
                        policy.policy_id,
                        policy.organization_id,
                        policy.version,

                        json.dumps(
                            policy.allowed_categories,
                            ensure_ascii=False,
                        ),

                        policy.amount_limit_minor,

                        json.dumps(
                            policy.category_limits_minor,
                            ensure_ascii=False,
                        ),

                        policy.receipt_required,

                        policy.submission_deadline_days,

                        json.dumps(
                            policy.allowed_currencies,
                            ensure_ascii=False,
                        ),

                        policy.active,

                        policy.created_at,
                        policy.updated_at,
                    ),
                )

            finally:
                cursor.close()

        return policy

    def get_active(
        self,
        *,
        organization_id: str,
    ) -> ReimbursementPolicy | None:

        sql = f"""
        SELECT *
        FROM {POLICY_TABLE}

        WHERE
            organization_id = %s
            AND
            active = TRUE

        ORDER BY
            version DESC

        LIMIT 1
        """

        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=False,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    organization_id,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return _from_row(
            dict(row)
        )

    def list_versions(
        self,
        *,
        organization_id: str,
    ) -> list[ReimbursementPolicy]:

        sql = f"""
        SELECT *
        FROM {POLICY_TABLE}

        WHERE
            organization_id = %s

        ORDER BY
            version DESC
        """

        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=False,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    organization_id,
                ),
            )

            rows = cursor.fetchall()

        return [
            _from_row(
                dict(row)
            )
            for row in rows
        ]
