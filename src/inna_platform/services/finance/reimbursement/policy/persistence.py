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
    POLICY_TABLE,
)

from .models import (
    ReimbursementPolicy,
)

from .repository import (
    PostgresReimbursementPolicyRepository,
    ReimbursementPolicyRepository,
)


POLICY_AUDIT_ACTION = (
    "reimbursement.policy.version.created"
)


def _audit_details(
    policy: ReimbursementPolicy,
) -> dict:

    return {
        "policy_id":
            policy.policy_id,

        "version":
            policy.version,

        "active":
            policy.active,

        "receipt_required":
            policy.receipt_required,

        "allowed_category_count":
            len(
                policy.allowed_categories
            ),

        "allowed_currency_count":
            len(
                policy.allowed_currencies
            ),

        "category_limit_count":
            len(
                policy.category_limits_minor
            ),

        "human_review_required":
            True,

        "automatic_approval":
            False,
    }


def _persist_postgres_atomic(
    *,
    organization_id: str,
    actor_user_id: str,
    allowed_categories: list[str],
    amount_limit_minor: int | None,
    category_limits_minor: dict[str, int],
    receipt_required: bool,
    submission_deadline_days: int | None,
    allowed_currencies: list[str],
) -> ReimbursementPolicy:

    with conexao_postgres(
        autocommit=False,
        commit_automatico=True,
    ) as connection:

        cursor = connection.cursor()

        try:

            #
            # Lock organization row so two administrators
            # cannot create the same next version concurrently.
            #
            cursor.execute(
                f"""
                SELECT organization_id
                FROM {ORGANIZATION_TABLE}

                WHERE
                    organization_id = %s
                    AND
                    active = TRUE

                FOR UPDATE
                """,
                (
                    organization_id,
                ),
            )

            if cursor.fetchone() is None:

                raise LookupError(
                    "ORGANIZATION_NOT_FOUND"
                )

            cursor.execute(
                f"""
                SELECT
                    COALESCE(
                        MAX(version),
                        0
                    )
                    +
                    1

                FROM {POLICY_TABLE}

                WHERE
                    organization_id = %s
                """,
                (
                    organization_id,
                ),
            )

            version_row = (
                cursor.fetchone()
            )

            next_version = int(
                version_row[0]
            )

            policy = ReimbursementPolicy(
                organization_id=
                    organization_id,

                version=
                    next_version,

                allowed_categories=
                    allowed_categories,

                amount_limit_minor=
                    amount_limit_minor,

                category_limits_minor=
                    category_limits_minor,

                receipt_required=
                    receipt_required,

                submission_deadline_days=
                    submission_deadline_days,

                allowed_currencies=
                    allowed_currencies,

                active=
                    True,
            )

            #
            # Only one active policy per organization.
            #
            cursor.execute(
                f"""
                UPDATE {POLICY_TABLE}

                SET
                    active = FALSE,
                    updated_at = NOW()

                WHERE
                    organization_id = %s
                    AND
                    active = TRUE
                """,
                (
                    organization_id,
                ),
            )

            cursor.execute(
                f"""
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
                """,
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

                    True,

                    policy.created_at,
                    policy.updated_at,
                ),
            )

            event = CorporateAuditEvent(
                organization_id=
                    organization_id,

                action=
                    POLICY_AUDIT_ACTION,

                actor_user_id=
                    actor_user_id,

                details=
                    _audit_details(
                        policy
                    ),
            )

            cursor.execute(
                f"""
                INSERT INTO {ORGANIZATION_AUDIT_TABLE} (
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
                """,
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

    return policy


def persist_new_policy_version(
    *,
    policy_repository:
        ReimbursementPolicyRepository,

    audit:
        CorporateAuditService
        |
        PostgresCorporateAuditService,

    organization_id: str,
    actor_user_id: str,

    allowed_categories: list[str],
    amount_limit_minor: int | None,
    category_limits_minor: dict[str, int],
    receipt_required: bool,
    submission_deadline_days: int | None,
    allowed_currencies: list[str],
) -> ReimbursementPolicy:

    postgres_policy = isinstance(
        policy_repository,
        PostgresReimbursementPolicyRepository,
    )

    postgres_audit = isinstance(
        audit,
        PostgresCorporateAuditService,
    )

    if (
        postgres_policy
        and
        postgres_audit
    ):

        return _persist_postgres_atomic(
            organization_id=
                organization_id,

            actor_user_id=
                actor_user_id,

            allowed_categories=
                allowed_categories,

            amount_limit_minor=
                amount_limit_minor,

            category_limits_minor=
                category_limits_minor,

            receipt_required=
                receipt_required,

            submission_deadline_days=
                submission_deadline_days,

            allowed_currencies=
                allowed_currencies,
        )

    if (
        postgres_policy
        !=
        postgres_audit
    ):

        raise RuntimeError(
            "MIXED_POLICY_PERSISTENCE_NOT_SUPPORTED"
        )

    versions = (
        policy_repository.list_versions(
            organization_id=
                organization_id,
        )
    )

    next_version = (
        max(
            (
                item.version
                for item
                in versions
            ),
            default=0,
        )
        +
        1
    )

    policy = ReimbursementPolicy(
        organization_id=
            organization_id,

        version=
            next_version,

        allowed_categories=
            allowed_categories,

        amount_limit_minor=
            amount_limit_minor,

        category_limits_minor=
            category_limits_minor,

        receipt_required=
            receipt_required,

        submission_deadline_days=
            submission_deadline_days,

        allowed_currencies=
            allowed_currencies,

        active=
            True,
    )

    policy_repository.save(
        policy
    )

    audit.record(
        organization_id=
            organization_id,

        action=
            POLICY_AUDIT_ACTION,

        actor_user_id=
            actor_user_id,

        details=
            _audit_details(
                policy
            ),
    )

    return policy
