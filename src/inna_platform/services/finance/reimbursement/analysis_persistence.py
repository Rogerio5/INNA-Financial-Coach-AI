from __future__ import annotations

import json

from typing import Any

from src.database.connection import (
    conexao_postgres,
)

from .audit.audit_service import (
    AuditEvent,
    PostgresReimbursementAuditService,
    ReimbursementAuditService,
)

from .db_schema import (
    REIMBURSEMENT_AUDIT_TABLE,
    REIMBURSEMENT_TABLE,
)

from .models import (
    ReimbursementRequest,
)

from .repository import (
    PostgresReimbursementRepository,
    ReimbursementRepository,
)


AUTO_APPROVAL_GATE_EVALUATED_ACTION = (
    "reimbursement."
    "auto_approval_gate."
    "evaluated"
)

REIMBURSEMENT_ANALYZED_ACTION = (
    "reimbursement.analyzed"
)


def analysis_persistence_capabilities() -> dict:

    return {
        "version":
            "reimbursement-2b10c6",

        "postgres_atomic_analysis_persistence":
            True,

        "atomic_reimbursement_update":
            True,

        "atomic_gate_audit":
            True,

        "atomic_analysis_audit":
            True,

        "rollback_on_failure":
            True,

        "no_partial_analysis_commit":
            True,

        "in_memory_fallback":
            True,

        "automatic_approval":
            False,

        "auto_transition_to_approved":
            False,

        "automatic_payment":
            False,

        "human_review_required":
            True,

        "document_content_trusted":
            False,
    }


def _insert_audit_event(
    *,
    cursor,
    event: AuditEvent,
) -> None:

    sql = f"""
    INSERT INTO {REIMBURSEMENT_AUDIT_TABLE}
    (
        event_id,
        tenant_id,
        reimbursement_id,
        action,
        actor_id,
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

    cursor.execute(
        sql,
        (
            event.event_id,
            event.tenant_id,
            event.reimbursement_id,
            event.action,
            event.actor_id,

            json.dumps(
                event.details,
                ensure_ascii=False,
                default=str,
            ),

            event.created_at,
        ),
    )


def _persist_postgres_atomic(
    *,
    reimbursement:
        ReimbursementRequest,

    gate_actor_id: str,

    gate_details:
        dict[str, Any],

    analysis_actor_id: str,

    analysis_details:
        dict[str, Any],
) -> ReimbursementRequest:

    update_sql = f"""
    UPDATE {REIMBURSEMENT_TABLE}

    SET
        status = %s,

        requires_human_review = %s,

        metadata = %s::jsonb,

        updated_at = %s

    WHERE
        tenant_id = %s
        AND
        reimbursement_id = %s

    RETURNING
        reimbursement_id
    """

    metadata_json = json.dumps(
        reimbursement.metadata,
        ensure_ascii=False,
        default=str,
    )


    gate_event = AuditEvent(
        tenant_id=
            reimbursement.tenant_id,

        reimbursement_id=
            reimbursement.id,

        action=
            AUTO_APPROVAL_GATE_EVALUATED_ACTION,

        actor_id=
            gate_actor_id,

        details=
            dict(
                gate_details
            ),
    )


    analysis_event = AuditEvent(
        tenant_id=
            reimbursement.tenant_id,

        reimbursement_id=
            reimbursement.id,

        action=
            REIMBURSEMENT_ANALYZED_ACTION,

        actor_id=
            analysis_actor_id,

        details=
            dict(
                analysis_details
            ),
    )


    with conexao_postgres(
        autocommit=False,
        commit_automatico=True,
    ) as connection:

        cursor = connection.cursor()

        try:

            # ------------------------------------------------
            # Persist the final analysis state.
            # ------------------------------------------------

            cursor.execute(
                update_sql,
                (
                    reimbursement.status.value,

                    reimbursement
                    .requires_human_review,

                    metadata_json,

                    reimbursement.updated_at,

                    reimbursement.tenant_id,

                    reimbursement.id,
                ),
            )


            row = cursor.fetchone()


            if row is None:

                raise LookupError(
                    "REIMBURSEMENT_ANALYSIS_SAVE_FAILED"
                )


            # ------------------------------------------------
            # Audit #1: governance gate decision.
            # ------------------------------------------------

            _insert_audit_event(
                cursor=
                    cursor,

                event=
                    gate_event,
            )


            # ------------------------------------------------
            # Audit #2: analysis completed.
            # ------------------------------------------------

            _insert_audit_event(
                cursor=
                    cursor,

                event=
                    analysis_event,
            )


        finally:

            cursor.close()


    return reimbursement


def _persist_repository_fallback(
    *,
    repository:
        ReimbursementRepository,

    audit:
        ReimbursementAuditService
        |
        PostgresReimbursementAuditService,

    reimbursement:
        ReimbursementRequest,

    gate_actor_id: str,

    gate_details:
        dict[str, Any],

    analysis_actor_id: str,

    analysis_details:
        dict[str, Any],
) -> ReimbursementRequest:
    """
    Compatibility path for unit/in-memory repositories.

    Durable transaction atomicity is guaranteed by the
    PostgreSQL path above.
    """

    saved = repository.save(
        reimbursement
    )


    audit.record(
        tenant_id=
            reimbursement.tenant_id,

        reimbursement_id=
            reimbursement.id,

        action=
            AUTO_APPROVAL_GATE_EVALUATED_ACTION,

        actor_id=
            gate_actor_id,

        details=
            gate_details,
    )


    audit.record(
        tenant_id=
            reimbursement.tenant_id,

        reimbursement_id=
            reimbursement.id,

        action=
            REIMBURSEMENT_ANALYZED_ACTION,

        actor_id=
            analysis_actor_id,

        details=
            analysis_details,
    )


    return saved


def persist_analysis_outcome(
    *,
    repository:
        ReimbursementRepository,

    audit:
        ReimbursementAuditService
        |
        PostgresReimbursementAuditService,

    reimbursement:
        ReimbursementRequest,

    gate_actor_id: str,

    gate_details:
        dict[str, Any],

    analysis_actor_id: str,

    analysis_details:
        dict[str, Any],
) -> ReimbursementRequest:
    """
    Final persistence boundary for analyze().

    Production PostgreSQL path commits as one unit:

        reimbursement state
        +
        auto approval gate audit
        +
        analyzed audit

    If any SQL operation fails, the transaction rolls
    back and no partial durable analysis is committed.
    """

    if (
        isinstance(
            repository,
            PostgresReimbursementRepository,
        )
        and
        isinstance(
            audit,
            PostgresReimbursementAuditService,
        )
    ):

        return _persist_postgres_atomic(
            reimbursement=
                reimbursement,

            gate_actor_id=
                gate_actor_id,

            gate_details=
                gate_details,

            analysis_actor_id=
                analysis_actor_id,

            analysis_details=
                analysis_details,
        )


    return _persist_repository_fallback(
        repository=
            repository,

        audit=
            audit,

        reimbursement=
            reimbursement,

        gate_actor_id=
            gate_actor_id,

        gate_details=
            gate_details,

        analysis_actor_id=
            analysis_actor_id,

        analysis_details=
            analysis_details,
    )