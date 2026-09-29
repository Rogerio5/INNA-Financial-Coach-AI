from __future__ import annotations

from src.database.connection import (
    cursor_postgres,
)


AUTO_APPROVAL_CONFIG_TABLE = (
    "finance_reimbursement_auto_approval_config"
)


def auto_approval_schema_statements(
) -> list[str]:

    return [
        f"""
        CREATE TABLE IF NOT EXISTS
            {AUTO_APPROVAL_CONFIG_TABLE}
        (
            organization_id TEXT PRIMARY KEY,

            enabled BOOLEAN
                NOT NULL
                DEFAULT FALSE,

            amount_limit_minor BIGINT NULL,

            version INTEGER
                NOT NULL
                DEFAULT 1,

            updated_by_user_id TEXT NULL,

            created_at TIMESTAMPTZ
                NOT NULL,

            updated_at TIMESTAMPTZ
                NOT NULL,

            CONSTRAINT
                chk_reimbursement_auto_approval_version
            CHECK (
                version >= 1
            ),

            CONSTRAINT
                chk_reimbursement_auto_approval_limit
            CHECK (
                amount_limit_minor IS NULL
                OR
                amount_limit_minor > 0
            ),

            CONSTRAINT
                chk_reimbursement_auto_approval_enabled_limit
            CHECK (
                enabled = FALSE
                OR
                amount_limit_minor IS NOT NULL
            )
        )
        """,

        f"""
        CREATE INDEX IF NOT EXISTS
            idx_reimbursement_auto_approval_enabled

        ON {AUTO_APPROVAL_CONFIG_TABLE}
            (enabled)
        """,
    ]


def ensure_auto_approval_schema(
) -> None:

    statements = (
        auto_approval_schema_statements()
    )

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        for statement in statements:

            cursor.execute(
                statement
            )


def auto_approval_capabilities(
) -> dict[str, object]:

    return {
        "version":
            "reimbursement-2b10c1",

        "organization_scoped":
            True,

        "default_disabled":
            True,

        "amount_limit_required_when_enabled":
            True,

        "persistent_configuration":
            True,

        "eligibility_required":
            True,

        "automatic_approval":
            False,

        "automatic_payment":
            False,

        "human_review_required":
            True,

        "self_approval":
            False,
    }