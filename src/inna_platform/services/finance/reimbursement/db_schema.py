from __future__ import annotations

from src.database.connection import cursor_postgres


REIMBURSEMENT_TABLE = "inna_finance_reimbursements"
REIMBURSEMENT_AUDIT_TABLE = "inna_finance_reimbursement_audit"

REIMBURSEMENT_IDEMPOTENCY_TABLE = (
    "inna_finance_reimbursement_idempotency"
)


def ensure_reimbursement_schema() -> None:
    reimbursement_sql = f"""
    CREATE TABLE IF NOT EXISTS {REIMBURSEMENT_TABLE} (
        reimbursement_id TEXT PRIMARY KEY,

        tenant_id TEXT NOT NULL,
        user_id TEXT NOT NULL,

        amount_minor BIGINT NOT NULL
            CHECK (amount_minor > 0),

        currency VARCHAR(3) NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,

        merchant TEXT NULL,
        expense_date DATE NULL,
        receipt_reference TEXT NULL,

        source_type TEXT NOT NULL DEFAULT 'finance',
        source_reference TEXT NULL,

        status TEXT NOT NULL DEFAULT 'draft',

        requires_human_review BOOLEAN
            NOT NULL
            DEFAULT TRUE,

        metadata JSONB
            NOT NULL
            DEFAULT '{{}}'::jsonb,

        submitted_at TIMESTAMPTZ NULL,

        created_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        updated_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        CHECK (
            status IN (
                'draft',
                'submitted',
                'analyzing',
                'needs_information',
                'awaiting_human_review',
                'approved',
                'rejected',
                'payment_pending',
                'paid',
                'cancelled'
            )
        ),

        CHECK (
            char_length(currency) = 3
        )
    )
    """

    audit_sql = f"""
    CREATE TABLE IF NOT EXISTS {REIMBURSEMENT_AUDIT_TABLE} (
        event_id TEXT PRIMARY KEY,

        tenant_id TEXT NOT NULL,
        reimbursement_id TEXT NOT NULL,

        action TEXT NOT NULL,
        actor_id TEXT NOT NULL,

        details JSONB
            NOT NULL
            DEFAULT '{{}}'::jsonb,

        created_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        CONSTRAINT fk_reimbursement_audit_request
            FOREIGN KEY (reimbursement_id)
            REFERENCES {REIMBURSEMENT_TABLE}
                (reimbursement_id)
            ON DELETE CASCADE
    )
    """

    idempotency_sql = f"""
    CREATE TABLE IF NOT EXISTS {REIMBURSEMENT_IDEMPOTENCY_TABLE} (
        tenant_id TEXT NOT NULL,
        reimbursement_id TEXT NOT NULL,
        key_hash CHAR(64) NOT NULL,

        operation TEXT NOT NULL,
        actor_id TEXT NOT NULL,
        payload_fingerprint CHAR(64) NOT NULL,

        response_snapshot JSONB NOT NULL,

        created_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        PRIMARY KEY (
            tenant_id,
            reimbursement_id,
            key_hash
        ),

        CONSTRAINT fk_reimbursement_idempotency_request
            FOREIGN KEY (reimbursement_id)
            REFERENCES {REIMBURSEMENT_TABLE}
                (reimbursement_id)
            ON DELETE CASCADE
    )
    """

    submitted_at_migration_sql = f"""
    ALTER TABLE {REIMBURSEMENT_TABLE}
    ADD COLUMN IF NOT EXISTS
        submitted_at TIMESTAMPTZ NULL
    """

    indexes = [
        f"""
        CREATE INDEX IF NOT EXISTS
            idx_reimbursement_tenant_user
        ON {REIMBURSEMENT_TABLE}
            (tenant_id, user_id)
        """,

        f"""
        CREATE INDEX IF NOT EXISTS
            idx_reimbursement_tenant_status
        ON {REIMBURSEMENT_TABLE}
            (tenant_id, status)
        """,

        f"""
        CREATE INDEX IF NOT EXISTS
            idx_reimbursement_created
        ON {REIMBURSEMENT_TABLE}
            (tenant_id, created_at DESC)
        """,

        f"""
        CREATE INDEX IF NOT EXISTS
            idx_reimbursement_audit_lookup
        ON {REIMBURSEMENT_AUDIT_TABLE}
            (tenant_id, reimbursement_id, created_at)
        """,
    ]

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            reimbursement_sql
        )

        cursor.execute(
            submitted_at_migration_sql
        )

        cursor.execute(
            audit_sql
        )

        cursor.execute(
            idempotency_sql
        )

        for sql in indexes:
            cursor.execute(sql)


def reimbursement_database_capabilities() -> dict:
    return {
        "version": "reimbursement-1b1",
        "postgresql": True,
        "persistent_requests": True,
        "persistent_audit": True,
        "tenant_scoped": True,
        "human_review_required": True,
        "automatic_approval": False,
    }