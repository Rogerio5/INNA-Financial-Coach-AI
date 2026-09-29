from __future__ import annotations

import hashlib
import hmac
import secrets

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from typing import Any
from uuid import uuid4

from src.database.connection import (
    cursor_postgres,
    obter_database_url,
)


IDENTITY_VERSION = "tc4-b2"

USER_TABLE = "inna_auth_users"

SESSION_TABLE = "inna_auth_sessions"

DEFAULT_SESSION_HOURS = 12


def _database_configured() -> bool:

    try:

        return bool(
            obter_database_url(
                obrigatoria=False
            )
        )

    except Exception:

        return False


def normalize_email(
    email: str,
) -> str:

    normalized = (
        str(
            email or ""
        )
        .strip()
        .lower()
    )

    if (
        not normalized
        or "@"
        not in normalized
    ):

        raise ValueError(
            "email inválido"
        )

    return normalized


def validate_password(
    password: str,
) -> str:

    value = str(
        password or ""
    )

    if len(value) < 10:

        raise ValueError(
            "password deve possuir ao menos 10 caracteres"
        )

    return value


def hash_password(
    password: str,
    *,
    salt_hex: str | None = None,
) -> tuple[str, str]:

    value = validate_password(
        password
    )

    if salt_hex:

        salt = bytes.fromhex(
            salt_hex
        )

    else:

        salt = secrets.token_bytes(
            16
        )

    derived = hashlib.scrypt(
        value.encode(
            "utf-8"
        ),
        salt=salt,
        n=16384,
        r=8,
        p=1,
        dklen=32,
    )

    return (
        salt.hex(),
        derived.hex(),
    )


def verify_password(
    password: str,
    *,
    salt_hex: str,
    expected_hash_hex: str,
) -> bool:

    try:

        _salt, calculated = hash_password(
            password,
            salt_hex=salt_hex,
        )

    except Exception:

        return False

    return hmac.compare_digest(
        calculated,
        expected_hash_hex,
    )


def hash_session_token(
    token: str,
) -> str:

    value = str(
        token or ""
    ).strip()

    if not value:

        raise ValueError(
            "session token vazio"
        )

    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def ensure_identity_schema() -> None:

    users_sql = f"""
    CREATE TABLE IF NOT EXISTS {USER_TABLE} (
        user_id TEXT PRIMARY KEY,

        email TEXT NOT NULL UNIQUE,

        password_salt TEXT NOT NULL,

        password_hash TEXT NOT NULL,

        active BOOLEAN NOT NULL
            DEFAULT TRUE,

        created_at TIMESTAMPTZ NOT NULL
            DEFAULT CURRENT_TIMESTAMP,

        updated_at TIMESTAMPTZ NOT NULL
            DEFAULT CURRENT_TIMESTAMP
    )
    """

    sessions_sql = f"""
    CREATE TABLE IF NOT EXISTS {SESSION_TABLE} (
        session_hash TEXT PRIMARY KEY,

        user_id TEXT NOT NULL
            REFERENCES {USER_TABLE}(user_id)
            ON DELETE CASCADE,

        created_at TIMESTAMPTZ NOT NULL
            DEFAULT CURRENT_TIMESTAMP,

        expires_at TIMESTAMPTZ NOT NULL,

        revoked_at TIMESTAMPTZ NULL,

        last_seen_at TIMESTAMPTZ NULL
    )
    """

    session_user_index = f"""
    CREATE INDEX IF NOT EXISTS
        idx_inna_auth_sessions_user
    ON {SESSION_TABLE} (
        user_id
    )
    """

    session_expiry_index = f"""
    CREATE INDEX IF NOT EXISTS
        idx_inna_auth_sessions_expiry
    ON {SESSION_TABLE} (
        expires_at
    )
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            users_sql
        )

        cursor.execute(
            sessions_sql
        )

        cursor.execute(
            session_user_index
        )

        cursor.execute(
            session_expiry_index
        )


def create_user(
    *,
    email: str,
    password: str,
    user_id: str | None = None,
) -> dict[str, Any]:

    ensure_identity_schema()

    normalized_email = normalize_email(
        email
    )

    password_salt, password_hash = (
        hash_password(
            password
        )
    )

    normalized_user_id = (
        str(
            user_id or ""
        ).strip()
        or uuid4().hex
    )

    sql = f"""
    INSERT INTO {USER_TABLE} (
        user_id,
        email,
        password_salt,
        password_hash,
        active
    )
    VALUES (
        %s,
        %s,
        %s,
        %s,
        TRUE
    )
    RETURNING
        user_id,
        email,
        active,
        created_at
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                normalized_user_id,
                normalized_email,
                password_salt,
                password_hash,
            ),
        )

        row = cursor.fetchone()

    return {
        "user_id": row[0],
        "email": row[1],
        "active": row[2],
        "created_at": row[3].isoformat(),
    }


def authenticate_user(
    *,
    email: str,
    password: str,
) -> dict[str, Any] | None:

    ensure_identity_schema()

    normalized_email = normalize_email(
        email
    )

    sql = f"""
    SELECT
        user_id,
        email,
        password_salt,
        password_hash,
        active
    FROM {USER_TABLE}
    WHERE email = %s
    LIMIT 1
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (
                normalized_email,
            ),
        )

        row = cursor.fetchone()

    if row is None:

        return None

    (
        user_id,
        stored_email,
        salt_hex,
        expected_hash,
        active,
    ) = row

    if not active:

        return None

    if not verify_password(
        password,
        salt_hex=salt_hex,
        expected_hash_hex=expected_hash,
    ):

        return None

    return {
        "user_id": user_id,
        "email": stored_email,
        "active": active,
    }


def create_session(
    *,
    user_id: str,
    session_hours: int = DEFAULT_SESSION_HOURS,
) -> dict[str, Any]:

    ensure_identity_schema()

    normalized_user_id = str(
        user_id or ""
    ).strip()

    if not normalized_user_id:

        raise ValueError(
            "user_id obrigatório"
        )

    hours = int(
        session_hours
    )

    if hours < 1:
        raise ValueError(
            "session_hours inválido"
        )

    raw_token = secrets.token_urlsafe(
        48
    )

    session_hash = hash_session_token(
        raw_token
    )

    expires_at = (
        datetime.now(
            timezone.utc
        )
        + timedelta(
            hours=hours
        )
    )

    sql = f"""
    INSERT INTO {SESSION_TABLE} (
        session_hash,
        user_id,
        expires_at
    )
    VALUES (
        %s,
        %s,
        %s
    )
    RETURNING
        created_at,
        expires_at
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                session_hash,
                normalized_user_id,
                expires_at,
            ),
        )

        row = cursor.fetchone()

    return {
        "session_token": raw_token,
        "user_id": normalized_user_id,
        "created_at": row[0].isoformat(),
        "expires_at": row[1].isoformat(),
    }


def resolve_session_user(
    session_token: str,
) -> dict[str, Any] | None:

    if not session_token:

        return None

    session_hash = hash_session_token(
        session_token
    )

    sql = f"""
    SELECT
        u.user_id,
        u.email,
        u.active,
        s.expires_at
    FROM {SESSION_TABLE} AS s
    INNER JOIN {USER_TABLE} AS u
        ON u.user_id = s.user_id
    WHERE s.session_hash = %s
      AND s.revoked_at IS NULL
      AND s.expires_at > CURRENT_TIMESTAMP
      AND u.active = TRUE
    LIMIT 1
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (
                session_hash,
            ),
        )

        row = cursor.fetchone()

    if row is None:

        return None

    return {
        "user_id": row[0],
        "email": row[1],
        "active": row[2],
        "expires_at": row[3].isoformat(),
    }


def revoke_session(
    session_token: str,
) -> bool:

    if not session_token:

        return False

    session_hash = hash_session_token(
        session_token
    )

    sql = f"""
    UPDATE {SESSION_TABLE}
    SET revoked_at = CURRENT_TIMESTAMP
    WHERE session_hash = %s
      AND revoked_at IS NULL
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                session_hash,
            ),
        )

        return (
            cursor.rowcount
            > 0
        )


def delete_user_for_validation(
    user_id: str,
) -> bool:

    normalized_user_id = str(
        user_id or ""
    ).strip()

    if not normalized_user_id:

        return False

    sql = f"""
    DELETE FROM {USER_TABLE}
    WHERE user_id = %s
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                normalized_user_id,
            ),
        )

        return (
            cursor.rowcount
            > 0
        )


def identity_capabilities() -> dict[str, Any]:

    return {
        "version": IDENTITY_VERSION,
        "database_configured": _database_configured(),
        "user_table": USER_TABLE,
        "session_table": SESSION_TABLE,
        "password_hashing": "scrypt",
        "session_token_random": True,
        "raw_session_token_stored": False,
        "server_session_lookup": True,
        "owner_identity_server_resolved": True,
        "browser_owner_id_allowed": False,
        "public_login_route": False,
        "public_registration_route": False,
        "finance_routes_protected": False,
        "http_only_cookie": "next_phase",
        "same_site_cookie": "next_phase",
        "personal_learning": False,
    }