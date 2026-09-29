from __future__ import annotations

from abc import ABC, abstractmethod

from src.database.connection import (
    cursor_postgres,
)

from .db_schema import (
    AUTO_APPROVAL_CONFIG_TABLE,
    ensure_auto_approval_schema,
)

from .models import (
    AutoApprovalConfiguration,
)


class AutoApprovalConfigurationRepository(
    ABC
):

    @abstractmethod
    def get(
        self,
        *,
        organization_id: str,
    ) -> AutoApprovalConfiguration | None:
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        config: AutoApprovalConfiguration,
    ) -> AutoApprovalConfiguration:
        raise NotImplementedError


class InMemoryAutoApprovalConfigurationRepository(
    AutoApprovalConfigurationRepository
):

    def __init__(self) -> None:

        self._items: dict[
            str,
            AutoApprovalConfiguration,
        ] = {}


    def get(
        self,
        *,
        organization_id: str,
    ) -> AutoApprovalConfiguration | None:

        return self._items.get(
            organization_id
        )


    def save(
        self,
        config: AutoApprovalConfiguration,
    ) -> AutoApprovalConfiguration:

        self._items[
            config.organization_id
        ] = config

        return config


def _from_row(
    row: dict,
) -> AutoApprovalConfiguration:

    return AutoApprovalConfiguration(
        organization_id=
            str(
                row["organization_id"]
            ),

        enabled=
            bool(
                row["enabled"]
            ),

        amount_limit_minor=
            (
                int(
                    row[
                        "amount_limit_minor"
                    ]
                )
                if row.get(
                    "amount_limit_minor"
                )
                is not None
                else None
            ),

        version=
            int(
                row["version"]
            ),

        updated_by_user_id=
            (
                str(
                    row[
                        "updated_by_user_id"
                    ]
                )
                if row.get(
                    "updated_by_user_id"
                )
                is not None
                else None
            ),

        created_at=
            row["created_at"],

        updated_at=
            row["updated_at"],
    )


class PostgresAutoApprovalConfigurationRepository(
    AutoApprovalConfigurationRepository
):

    def __init__(self) -> None:

        ensure_auto_approval_schema()


    def get(
        self,
        *,
        organization_id: str,
    ) -> AutoApprovalConfiguration | None:

        sql = f"""
        SELECT
            organization_id,
            enabled,
            amount_limit_minor,
            version,
            updated_by_user_id,
            created_at,
            updated_at

        FROM {AUTO_APPROVAL_CONFIG_TABLE}

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
                    organization_id,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return _from_row(
            dict(row)
        )


    def save(
        self,
        config: AutoApprovalConfiguration,
    ) -> AutoApprovalConfiguration:

        sql = f"""
        INSERT INTO
            {AUTO_APPROVAL_CONFIG_TABLE}
        (
            organization_id,
            enabled,
            amount_limit_minor,
            version,
            updated_by_user_id,
            created_at,
            updated_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )

        ON CONFLICT (
            organization_id
        )
        DO UPDATE SET
            enabled =
                EXCLUDED.enabled,

            amount_limit_minor =
                EXCLUDED.amount_limit_minor,

            version =
                EXCLUDED.version,

            updated_by_user_id =
                EXCLUDED.updated_by_user_id,

            updated_at =
                EXCLUDED.updated_at
        """

        with cursor_postgres(
            dict_cursor=False,
            commit_automatico=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    config.organization_id,
                    config.enabled,
                    config.amount_limit_minor,
                    config.version,
                    config.updated_by_user_id,
                    config.created_at,
                    config.updated_at,
                ),
            )

        return config