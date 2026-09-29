from __future__ import annotations

import json

from src.database.connection import (
    conexao_postgres,
)

from ..corporate.audit import (
    CorporateAuditEvent,
    CorporateAuditService,
    PostgresCorporateAuditService,
)

from ..corporate.db_schema import (
    ORGANIZATION_AUDIT_TABLE,
    ORGANIZATION_TABLE,
)

from .db_schema import (
    AUTO_APPROVAL_CONFIG_TABLE,
)

from .models import (
    AutoApprovalConfiguration,
    utc_now,
)

from .repository import (
    AutoApprovalConfigurationRepository,
    PostgresAutoApprovalConfigurationRepository,
)


CONFIG_UPDATED_ACTION = (
    "reimbursement."
    "auto_approval."
    "configuration.updated"
)


def _normalize_expected_version(
    expected_version: int | None,
) -> int | None:

    if expected_version is None:
        return None

    try:
        value = int(
            expected_version
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            "AUTO_APPROVAL_EXPECTED_VERSION_INVALID"
        ) from exc

    if value < 0:

        raise ValueError(
            "AUTO_APPROVAL_EXPECTED_VERSION_INVALID"
        )

    return value


def _assert_expected_version(
    *,
    current:
        AutoApprovalConfiguration
        |
        None,

    expected_version:
        int
        |
        None,
) -> None:

    expected_version = (
        _normalize_expected_version(
            expected_version
        )
    )

    if expected_version is None:
        return

    current_version = (
        0
        if current is None
        else current.version
    )

    if (
        expected_version
        !=
        current_version
    ):

        raise ValueError(
            "AUTO_APPROVAL_VERSION_CONFLICT"
        )


def _build_configuration(
    *,
    organization_id: str,
    actor_user_id: str,
    enabled: bool,
    amount_limit_minor: int | None,
    current:
        AutoApprovalConfiguration
        |
        None,
) -> AutoApprovalConfiguration:

    now = utc_now()

    version = (
        1
        if current is None
        else current.version + 1
    )

    return AutoApprovalConfiguration(
        organization_id=
            organization_id,

        enabled=
            bool(enabled),

        amount_limit_minor=
            amount_limit_minor,

        version=
            version,

        updated_by_user_id=
            actor_user_id,

        created_at=
            (
                current.created_at
                if current is not None
                else now
            ),

        updated_at=
            now,
    )


def _audit_details(
    *,
    config:
        AutoApprovalConfiguration,

    previous_version: int,

    expected_version:
        int
        |
        None,
) -> dict:

    return {
        "enabled":
            config.enabled,

        "amount_limit_minor":
            config.amount_limit_minor,

        "previous_version":
            previous_version,

        "version":
            config.version,

        "expected_version":
            expected_version,

        "atomic_persistence":
            True,

        "automatic_approval":
            False,

        "automatic_payment":
            False,

        "human_review_required":
            True,
    }


def _persist_postgres_atomic(
    *,
    organization_id: str,
    actor_user_id: str,
    enabled: bool,
    amount_limit_minor: int | None,
    expected_version: int | None,
) -> AutoApprovalConfiguration:

    lock_org_sql = f"""
    SELECT
        organization_id

    FROM {ORGANIZATION_TABLE}

    WHERE
        organization_id = %s

    FOR UPDATE
    """

    get_config_sql = f"""
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

    FOR UPDATE
    """

    save_config_sql = f"""
    INSERT INTO {AUTO_APPROVAL_CONFIG_TABLE}
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

    save_audit_sql = f"""
    INSERT INTO {ORGANIZATION_AUDIT_TABLE}
    (
        event_id,
        organization_id,
        action,
        actor_user_id,
        target_user_id,
        details,
        created_at
    )
    VALUES (
        %s,
        %s,
        %s,
        %s,
        %s,
        %s::jsonb,
        %s
    )
    """

    with conexao_postgres(
        autocommit=False,
        commit_automatico=True,
    ) as connection:

        cursor = connection.cursor()

        try:

            # ------------------------------------------------
            # Lock the organization first.
            #
            # This serializes configuration creation/update
            # even when the config row does not yet exist.
            # ------------------------------------------------

            cursor.execute(
                lock_org_sql,
                (
                    organization_id,
                ),
            )

            organization_row = (
                cursor.fetchone()
            )

            if organization_row is None:

                raise LookupError(
                    "AUTO_APPROVAL_ORGANIZATION_NOT_FOUND"
                )


            # ------------------------------------------------
            # Lock current configuration.
            # ------------------------------------------------

            cursor.execute(
                get_config_sql,
                (
                    organization_id,
                ),
            )

            row = cursor.fetchone()

            current = None

            if row is not None:

                current = (
                    AutoApprovalConfiguration(
                        organization_id=
                            str(
                                row[0]
                            ),

                        enabled=
                            bool(
                                row[1]
                            ),

                        amount_limit_minor=
                            (
                                int(
                                    row[2]
                                )
                                if row[2]
                                is not None
                                else None
                            ),

                        version=
                            int(
                                row[3]
                            ),

                        updated_by_user_id=
                            (
                                str(
                                    row[4]
                                )
                                if row[4]
                                is not None
                                else None
                            ),

                        created_at=
                            row[5],

                        updated_at=
                            row[6],
                    )
                )


            _assert_expected_version(
                current=
                    current,

                expected_version=
                    expected_version,
            )


            config = (
                _build_configuration(
                    organization_id=
                        organization_id,

                    actor_user_id=
                        actor_user_id,

                    enabled=
                        enabled,

                    amount_limit_minor=
                        amount_limit_minor,

                    current=
                        current,
                )
            )


            cursor.execute(
                save_config_sql,
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


            event = CorporateAuditEvent(
                organization_id=
                    organization_id,

                action=
                    CONFIG_UPDATED_ACTION,

                actor_user_id=
                    actor_user_id,

                details=
                    _audit_details(
                        config=config,

                        previous_version=
                            (
                                0
                                if current is None
                                else current.version
                            ),

                        expected_version=
                            expected_version,
                    ),
            )


            cursor.execute(
                save_audit_sql,
                (
                    event.event_id,
                    event.organization_id,
                    event.action,
                    event.actor_user_id,
                    event.target_user_id,

                    json.dumps(
                        event.details,
                        ensure_ascii=False,
                        default=str,
                    ),

                    event.created_at,
                ),
            )

        finally:

            cursor.close()


    return config


def _persist_repository_fallback(
    *,
    repository:
        AutoApprovalConfigurationRepository,

    audit:
        CorporateAuditService,

    organization_id: str,

    actor_user_id: str,

    enabled: bool,

    amount_limit_minor: int | None,

    expected_version: int | None,
) -> AutoApprovalConfiguration:

    current = repository.get(
        organization_id=
            organization_id
    )

    _assert_expected_version(
        current=
            current,

        expected_version=
            expected_version,
    )

    config = _build_configuration(
        organization_id=
            organization_id,

        actor_user_id=
            actor_user_id,

        enabled=
            enabled,

        amount_limit_minor=
            amount_limit_minor,

        current=
            current,
    )

    saved = repository.save(
        config
    )

    audit.record(
        organization_id=
            organization_id,

        action=
            CONFIG_UPDATED_ACTION,

        actor_user_id=
            actor_user_id,

        details=
            _audit_details(
                config=saved,

                previous_version=
                    (
                        0
                        if current is None
                        else current.version
                    ),

                expected_version=
                    expected_version,
            ),
    )

    return saved


def persist_auto_approval_configuration(
    *,
    repository:
        AutoApprovalConfigurationRepository,

    audit:
        CorporateAuditService,

    organization_id: str,

    actor_user_id: str,

    enabled: bool,

    amount_limit_minor: int | None,

    expected_version:
        int
        |
        None
        =
        None,
) -> AutoApprovalConfiguration:
    """
    Persists configuration with version protection.

    PostgreSQL production path:
    - locks organization row;
    - locks current config row;
    - calculates next version inside transaction;
    - writes config;
    - writes corporate audit;
    - commits both together;
    - rolls both back on error.

    In-memory/test repositories preserve the same
    version semantics without claiming database
    transactionality.
    """

    organization_id = str(
        organization_id or ""
    ).strip()

    actor_user_id = str(
        actor_user_id or ""
    ).strip()

    if not organization_id:

        raise ValueError(
            "AUTO_APPROVAL_ORGANIZATION_REQUIRED"
        )

    if not actor_user_id:

        raise ValueError(
            "AUTO_APPROVAL_ACTOR_REQUIRED"
        )


    normalized_expected = (
        _normalize_expected_version(
            expected_version
        )
    )


    if (
        isinstance(
            repository,
            PostgresAutoApprovalConfigurationRepository,
        )
        and
        isinstance(
            audit,
            PostgresCorporateAuditService,
        )
    ):

        return _persist_postgres_atomic(
            organization_id=
                organization_id,

            actor_user_id=
                actor_user_id,

            enabled=
                enabled,

            amount_limit_minor=
                amount_limit_minor,

            expected_version=
                normalized_expected,
        )


    return _persist_repository_fallback(
        repository=
            repository,

        audit=
            audit,

        organization_id=
            organization_id,

        actor_user_id=
            actor_user_id,

        enabled=
            enabled,

        amount_limit_minor=
            amount_limit_minor,

        expected_version=
            normalized_expected,
    )