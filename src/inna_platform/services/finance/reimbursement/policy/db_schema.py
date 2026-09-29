from __future__ import annotations

from src.database.connection import (
    cursor_postgres,
)

from ..corporate.db_schema import (
    ORGANIZATION_TABLE,
    ensure_corporate_schema,
)


POLICY_TABLE = (
    "inna_finance_reimbursement_policies"
)


def ensure_policy_schema() -> None:

    ensure_corporate_schema()

    table_sql = f"""
    CREATE TABLE IF NOT EXISTS {POLICY_TABLE} (

        policy_id TEXT PRIMARY KEY,

        organization_id TEXT NOT NULL,

        version INTEGER NOT NULL,

        allowed_categories JSONB
            NOT NULL
            DEFAULT '[]'::jsonb,

        amount_limit_minor BIGINT NULL,

        category_limits_minor JSONB
            NOT NULL
            DEFAULT '{{}}'::jsonb,

        receipt_required BOOLEAN
            NOT NULL
            DEFAULT TRUE,

        submission_deadline_days INTEGER NULL,

        allowed_currencies JSONB
            NOT NULL
            DEFAULT '["BRL"]'::jsonb,

        active BOOLEAN
            NOT NULL
            DEFAULT TRUE,

        created_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        updated_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        CONSTRAINT fk_reimbursement_policy_org
            FOREIGN KEY (organization_id)
            REFERENCES {ORGANIZATION_TABLE}
                (organization_id)
            ON DELETE CASCADE,

        CONSTRAINT uq_reimbursement_policy_version
            UNIQUE (
                organization_id,
                version
            ),

        CHECK (
            amount_limit_minor IS NULL
            OR
            amount_limit_minor > 0
        ),

        CHECK (
            submission_deadline_days IS NULL
            OR
            submission_deadline_days >= 0
        )
    )
    """

    active_index_sql = f"""
    CREATE UNIQUE INDEX IF NOT EXISTS
        uq_reimbursement_policy_active_org

    ON {POLICY_TABLE} (
        organization_id
    )

    WHERE active = TRUE
    """

    lookup_index_sql = f"""
    CREATE INDEX IF NOT EXISTS
        idx_reimbursement_policy_versions

    ON {POLICY_TABLE} (
        organization_id,
        version DESC
    )
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            table_sql
        )

        cursor.execute(
            active_index_sql
        )

        cursor.execute(
            lookup_index_sql
        )


def policy_capabilities() -> dict:

    return {
        "version":
            "reimbursement-2b7b",

        "organization_scoped":
            True,

        "persistent_policy":
            True,

        "versioned_policy":
            True,

        "single_active_policy":
            True,

        "allowed_categories":
            True,

        "general_amount_limit":
            True,

        "category_amount_limits":
            True,

        "receipt_requirement":
            True,

        "submission_deadline":
            True,

        "allowed_currencies":
            True,

        "policy_findings":
            True,

        "policy_admin_api":
            True,

        "organization_admin_only":
            True,

        "organization_id_from_browser":
            False,

        "policy_version_from_browser":
            False,

        "policy_audit":
            True,

        "atomic_policy_and_audit":
            True,

        "human_review_required":
            True,

        "automatic_approval":
            False,
    }
