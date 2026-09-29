from __future__ import annotations

from src.database.connection import cursor_postgres


ORGANIZATION_TABLE = (
    "inna_finance_organizations"
)

ORGANIZATION_MEMBER_TABLE = (
    "inna_finance_organization_members"
)

ORGANIZATION_AUDIT_TABLE = (
    "inna_finance_organization_audit"
)


def ensure_corporate_schema() -> None:

    organization_sql = f"""
    CREATE TABLE IF NOT EXISTS {ORGANIZATION_TABLE} (
        organization_id TEXT PRIMARY KEY,

        name TEXT NOT NULL,

        created_by_user_id TEXT NOT NULL,

        active BOOLEAN
            NOT NULL
            DEFAULT TRUE,

        created_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        updated_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW()
    )
    """

    member_sql = f"""
    CREATE TABLE IF NOT EXISTS {ORGANIZATION_MEMBER_TABLE} (
        organization_id TEXT NOT NULL,

        user_id TEXT NOT NULL,

        role TEXT NOT NULL,

        active BOOLEAN
            NOT NULL
            DEFAULT TRUE,

        created_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        updated_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        PRIMARY KEY (
            organization_id,
            user_id
        ),

        CONSTRAINT fk_finance_org_member_org
            FOREIGN KEY (organization_id)
            REFERENCES {ORGANIZATION_TABLE}
                (organization_id)
            ON DELETE CASCADE,

        CHECK (
            role IN (
                'employee',
                'manager',
                'finance_approver',
                'organization_admin'
            )
        )
    )
    """

    audit_sql = f"""
    CREATE TABLE IF NOT EXISTS {ORGANIZATION_AUDIT_TABLE} (
        event_id TEXT PRIMARY KEY,

        organization_id TEXT NOT NULL,

        action TEXT NOT NULL,

        actor_user_id TEXT NOT NULL,

        target_user_id TEXT NULL,

        details JSONB
            NOT NULL
            DEFAULT '{{}}'::jsonb,

        created_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        CONSTRAINT fk_finance_org_audit_org
            FOREIGN KEY (organization_id)
            REFERENCES {ORGANIZATION_TABLE}
                (organization_id)
            ON DELETE CASCADE
    )
    """

    indexes = [
        f"""
        CREATE INDEX IF NOT EXISTS
            idx_finance_org_members_user
        ON {ORGANIZATION_MEMBER_TABLE}
            (user_id, active)
        """,

        f"""
        CREATE INDEX IF NOT EXISTS
            idx_finance_org_members_role
        ON {ORGANIZATION_MEMBER_TABLE}
            (organization_id, role, active)
        """,

        f"""
        CREATE INDEX IF NOT EXISTS
            idx_finance_org_audit_org
        ON {ORGANIZATION_AUDIT_TABLE}
            (organization_id, created_at DESC)
        """,
    ]

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            organization_sql
        )

        cursor.execute(
            member_sql
        )

        cursor.execute(
            audit_sql
        )

        for sql in indexes:
            cursor.execute(sql)


def corporate_capabilities() -> dict:

    return {
        "version":
            "reimbursement-1b3d",

        "organizations":
            True,

        "memberships":
            True,

        "roles":
            True,

        "finance_approver_role":
            True,

        "organization_admin_role":
            True,

        "member_management":
            True,

        "persistent_organization_audit":
            True,

        "organization_id_from_browser":
            False,

        "browser_role_assignment":
            False,

        "self_role_change":
            False,

        "self_deactivation":
            False,

        "self_approval":
            False,
    }