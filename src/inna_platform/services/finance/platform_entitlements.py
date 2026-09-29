from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.inna_platform.services.finance.transaction_repository import (
    cursor_postgres,
)


ENTITLEMENT_TABLE = (
    "inna_user_platform_entitlements"
)

VALID_STATUSES = {
    "active",
    "pending",
    "cancelled",
    "expired",
}


def _normalize_text(
    value: Any,
) -> str:

    if value is None:
        return ""

    return str(
        value
    ).strip()


def _normalize_code(
    value: Any,
) -> str:

    return (
        _normalize_text(
            value
        )
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def _normalize_expires_at(
    value: Any,
):

    if value in (
        None,
        "",
    ):
        return None

    if isinstance(
        value,
        datetime,
    ):

        result = value

    else:

        raw = (
            str(value)
            .strip()
            .replace(
                "Z",
                "+00:00",
            )
        )

        result = (
            datetime.fromisoformat(
                raw
            )
        )

    if result.tzinfo is None:

        result = result.replace(
            tzinfo=timezone.utc,
        )

    return result


def _row_to_dict(
    row,
) -> dict[str, Any] | None:

    if row is None:
        return None

    columns = (
        "entitlement_id",
        "user_id",
        "platform_code",
        "plan_code",
        "status",
        "activated_at",
        "expires_at",
        "created_at",
        "updated_at",
    )

    return dict(
        zip(
            columns,
            row,
        )
    )


def ensure_entitlement_schema() -> None:

    sql = f"""
    CREATE TABLE IF NOT EXISTS {ENTITLEMENT_TABLE} (
        entitlement_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        platform_code TEXT NOT NULL,
        plan_code TEXT NOT NULL,
        status TEXT NOT NULL,
        activated_at TIMESTAMPTZ NULL,
        expires_at TIMESTAMPTZ NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

        CONSTRAINT
            uq_inna_user_platform_entitlement
        UNIQUE (
            user_id,
            platform_code
        ),

        CONSTRAINT
            ck_inna_platform_entitlement_status
        CHECK (
            status IN (
                'active',
                'pending',
                'cancelled',
                'expired'
            )
        )
    )
    """

    index_sql = f"""
    CREATE INDEX IF NOT EXISTS
        idx_inna_entitlements_user_status
    ON {ENTITLEMENT_TABLE} (
        user_id,
        status
    )
    """

    platform_index_sql = f"""
    CREATE INDEX IF NOT EXISTS
        idx_inna_entitlements_platform_status
    ON {ENTITLEMENT_TABLE} (
        platform_code,
        status
    )
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql
        )

        cursor.execute(
            index_sql
        )

        cursor.execute(
            platform_index_sql
        )


def _assert_active_user(
    user_id: str,
) -> None:

    sql = """
    SELECT 1
    FROM inna_auth_users
    WHERE user_id = %s
      AND active = TRUE
    LIMIT 1
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (
                user_id,
            ),
        )

        row = cursor.fetchone()

    if row is None:

        raise ValueError(
            "usuário inexistente ou inativo"
        )


def grant_platform_entitlement(
    *,
    user_id: str,
    platform_code: str,
    plan_code: str,
    status: str = "active",
    expires_at: Any = None,
) -> dict[str, Any]:

    normalized_user_id = (
        _normalize_text(
            user_id
        )
    )

    normalized_platform = (
        _normalize_code(
            platform_code
        )
    )

    normalized_plan = (
        _normalize_code(
            plan_code
        )
    )

    normalized_status = (
        _normalize_code(
            status
        )
    )

    if not normalized_user_id:

        raise ValueError(
            "user_id é obrigatório"
        )

    if not normalized_platform:

        raise ValueError(
            "platform_code é obrigatório"
        )

    if not normalized_plan:

        raise ValueError(
            "plan_code é obrigatório"
        )

    if (
        normalized_status
        not in VALID_STATUSES
    ):

        raise ValueError(
            "status de entitlement inválido"
        )

    normalized_expires_at = (
        _normalize_expires_at(
            expires_at
        )
    )

    ensure_entitlement_schema()

    _assert_active_user(
        normalized_user_id
    )

    entitlement_id = (
        uuid4().hex
    )

    sql = f"""
    INSERT INTO {ENTITLEMENT_TABLE} (
        entitlement_id,
        user_id,
        platform_code,
        plan_code,
        status,
        activated_at,
        expires_at
    )
    VALUES (
        %s,
        %s,
        %s,
        %s,
        %s,
        CASE
            WHEN %s = 'active'
            THEN NOW()
            ELSE NULL
        END,
        %s
    )

    ON CONFLICT (
        user_id,
        platform_code
    )

    DO UPDATE SET
        plan_code =
            EXCLUDED.plan_code,

        status =
            EXCLUDED.status,

        activated_at =
            CASE
                WHEN EXCLUDED.status = 'active'
                THEN COALESCE(
                    {ENTITLEMENT_TABLE}.activated_at,
                    NOW()
                )
                ELSE
                    {ENTITLEMENT_TABLE}.activated_at
            END,

        expires_at =
            EXCLUDED.expires_at,

        updated_at =
            NOW()

    RETURNING
        entitlement_id,
        user_id,
        platform_code,
        plan_code,
        status,
        activated_at,
        expires_at,
        created_at,
        updated_at
    """

    params = (
        entitlement_id,
        normalized_user_id,
        normalized_platform,
        normalized_plan,
        normalized_status,
        normalized_status,
        normalized_expires_at,
    )

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            params,
        )

        row = cursor.fetchone()

    result = _row_to_dict(
        row
    )

    if result is None:

        raise RuntimeError(
            "entitlement não retornado pelo PostgreSQL"
        )

    return result


def get_platform_entitlement(
    *,
    user_id: str,
    platform_code: str,
) -> dict[str, Any] | None:

    ensure_entitlement_schema()

    normalized_user_id = (
        _normalize_text(
            user_id
        )
    )

    normalized_platform = (
        _normalize_code(
            platform_code
        )
    )

    sql = f"""
    SELECT
        entitlement_id,
        user_id,
        platform_code,
        plan_code,
        status,
        activated_at,
        expires_at,
        created_at,
        updated_at
    FROM {ENTITLEMENT_TABLE}
    WHERE user_id = %s
      AND platform_code = %s
    LIMIT 1
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (
                normalized_user_id,
                normalized_platform,
            ),
        )

        row = cursor.fetchone()

    return _row_to_dict(
        row
    )


def is_entitlement_active(
    entitlement: dict[str, Any] | None,
) -> bool:

    if entitlement is None:
        return False

    if (
        entitlement.get(
            "status"
        )
        != "active"
    ):
        return False

    expires_at = entitlement.get(
        "expires_at"
    )

    if expires_at is None:
        return True

    if expires_at.tzinfo is None:

        expires_at = expires_at.replace(
            tzinfo=timezone.utc,
        )

    return (
        expires_at
        >
        datetime.now(
            timezone.utc
        )
    )


def has_active_platform_entitlement(
    *,
    user_id: str,
    platform_code: str,
) -> bool:

    entitlement = (
        get_platform_entitlement(
            user_id=user_id,
            platform_code=platform_code,
        )
    )

    return is_entitlement_active(
        entitlement
    )


def list_user_entitlements(
    *,
    user_id: str,
) -> list[dict[str, Any]]:

    ensure_entitlement_schema()

    normalized_user_id = (
        _normalize_text(
            user_id
        )
    )

    sql = f"""
    SELECT
        entitlement_id,
        user_id,
        platform_code,
        plan_code,
        status,
        activated_at,
        expires_at,
        created_at,
        updated_at
    FROM {ENTITLEMENT_TABLE}
    WHERE user_id = %s
    ORDER BY
        platform_code ASC
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (
                normalized_user_id,
            ),
        )

        rows = cursor.fetchall()

    return [
        _row_to_dict(
            row
        )
        for row in rows
    ]


def revoke_platform_entitlement(
    *,
    user_id: str,
    platform_code: str,
) -> bool:

    ensure_entitlement_schema()

    normalized_user_id = (
        _normalize_text(
            user_id
        )
    )

    normalized_platform = (
        _normalize_code(
            platform_code
        )
    )

    sql = f"""
    UPDATE {ENTITLEMENT_TABLE}
    SET
        status = 'cancelled',
        updated_at = NOW()
    WHERE user_id = %s
      AND platform_code = %s
    RETURNING entitlement_id
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                normalized_user_id,
                normalized_platform,
            ),
        )

        row = cursor.fetchone()

    return row is not None


def delete_platform_entitlement_for_validation(
    *,
    user_id: str,
    platform_code: str,
) -> bool:

    ensure_entitlement_schema()

    normalized_user_id = (
        _normalize_text(
            user_id
        )
    )

    normalized_platform = (
        _normalize_code(
            platform_code
        )
    )

    sql = f"""
    DELETE FROM {ENTITLEMENT_TABLE}
    WHERE user_id = %s
      AND platform_code = %s
    RETURNING entitlement_id
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                normalized_user_id,
                normalized_platform,
            ),
        )

        row = cursor.fetchone()

    return row is not None


def platform_entitlement_capabilities() -> dict[str, Any]:

    return {
        "version": "tc4-d2a",
        "table": ENTITLEMENT_TABLE,
        "persistence": "postgresql",
        "platform_entitlements": True,
        "per_user": True,
        "per_platform": True,
        "plan_code": True,
        "status": True,
        "expiration": True,
        "active_check": True,
        "financeiro_supported": True,
        "demo_requires_entitlement": False,
        "real_platform_requires_entitlement": True,
        "checkout_activation_connected": False,
        "financeiro_route_protected": False,
        "browser_can_grant_entitlement": False,
    }