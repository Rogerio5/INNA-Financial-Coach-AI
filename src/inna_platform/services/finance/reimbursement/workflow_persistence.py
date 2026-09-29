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
    REIMBURSEMENT_IDEMPOTENCY_TABLE,
    REIMBURSEMENT_TABLE,
)

from .idempotency import (
    IdempotencyContext,
    assert_replay_compatible,
    build_idempotency_context,
    database_row_snapshot,
    decode_json_object,
    reimbursement_from_snapshot,
    reimbursement_snapshot,
)

from .models import (
    ReimbursementRequest,
    ReimbursementStatus,
    utc_now,
)

from .repository import (
    PostgresReimbursementRepository,
    ReimbursementRepository,
)

from .workflow import (
    assert_transition,
    transition_reimbursement,
)


WORKFLOW_PERSISTENCE_VERSION = (
    "reimbursement-2b8b"
)


WORKFLOW_AUDIT_ACTIONS: dict[
    tuple[
        ReimbursementStatus,
        ReimbursementStatus,
    ],
    str,
] = {

    (
        ReimbursementStatus.DRAFT,
        ReimbursementStatus.SUBMITTED,
    ):
        "reimbursement.submitted",

    (
        ReimbursementStatus.NEEDS_INFORMATION,
        ReimbursementStatus.SUBMITTED,
    ):
        "reimbursement.resubmitted",

    (
        ReimbursementStatus.SUBMITTED,
        ReimbursementStatus.ANALYZING,
    ):
        "reimbursement.analysis_started",

    (
        ReimbursementStatus.ANALYZING,
        ReimbursementStatus.NEEDS_INFORMATION,
    ):
        "reimbursement.analyzed",

    (
        ReimbursementStatus.ANALYZING,
        ReimbursementStatus.AWAITING_HUMAN_REVIEW,
    ):
        "reimbursement.analyzed",

    (
        ReimbursementStatus.AWAITING_HUMAN_REVIEW,
        ReimbursementStatus.APPROVED,
    ):
        "reimbursement.human_review",

    (
        ReimbursementStatus.AWAITING_HUMAN_REVIEW,
        ReimbursementStatus.REJECTED,
    ):
        "reimbursement.human_review",

    (
        ReimbursementStatus.AWAITING_HUMAN_REVIEW,
        ReimbursementStatus.NEEDS_INFORMATION,
    ):
        "reimbursement.human_review",

    (
        ReimbursementStatus.DRAFT,
        ReimbursementStatus.CANCELLED,
    ):
        "reimbursement.cancelled",

    (
        ReimbursementStatus.SUBMITTED,
        ReimbursementStatus.CANCELLED,
    ):
        "reimbursement.cancelled",

    (
        ReimbursementStatus.NEEDS_INFORMATION,
        ReimbursementStatus.CANCELLED,
    ):
        "reimbursement.cancelled",

    (
        ReimbursementStatus.AWAITING_HUMAN_REVIEW,
        ReimbursementStatus.CANCELLED,
    ):
        "reimbursement.cancelled",

    (
        ReimbursementStatus.APPROVED,
        ReimbursementStatus.PAYMENT_PENDING,
    ):
        "reimbursement.payment_pending",

    (
        ReimbursementStatus.PAYMENT_PENDING,
        ReimbursementStatus.PAID,
    ):
        "reimbursement.paid",
}


def audit_action_for_transition(
    *,
    current_status: ReimbursementStatus,
    target_status: ReimbursementStatus,
) -> str:

    assert_transition(
        current_status=
            current_status,

        target_status=
            target_status,
    )

    action = (
        WORKFLOW_AUDIT_ACTIONS.get(
            (
                current_status,
                target_status,
            )
        )
    )

    if action is None:

        raise ValueError(
            "REIMBURSEMENT_AUDIT_ACTION_NOT_CONFIGURED"
        )

    return action


def _safe_details(
    *,
    current_status: ReimbursementStatus,
    target_status: ReimbursementStatus,
    details: dict[str, Any] | None,
) -> dict[str, Any]:

    safe = dict(
        details or {}
    )

    #
    # These fields are server-derived and cannot
    # be overridden by caller-provided details.
    #
    safe[
        "from_status"
    ] = current_status.value

    safe[
        "to_status"
    ] = target_status.value

    safe[
        "workflow_version"
    ] = WORKFLOW_PERSISTENCE_VERSION

    safe[
        "automatic_approval"
    ] = False

    return safe



def _persist_postgres_atomic(
    *,
    repository: PostgresReimbursementRepository,
    tenant_id: str,
    reimbursement_id: str,
    actor_id: str,
    target_status: ReimbursementStatus,
    details: dict[str, Any] | None,
    idempotency: IdempotencyContext | None,
) -> ReimbursementRequest:

    response_snapshot = None

    with conexao_postgres(
        autocommit=False,
        commit_automatico=True,
    ) as connection:

        cursor = connection.cursor()

        try:

            #
            # One reimbursement row lock serializes both normal
            # transitions and idempotent retries for the same
            # reimbursement.
            #
            cursor.execute(
                f"""
                SELECT
                    to_jsonb(r)

                FROM {REIMBURSEMENT_TABLE}
                    AS r

                WHERE
                    tenant_id = %s
                    AND
                    reimbursement_id = %s

                FOR UPDATE
                """,
                (
                    tenant_id,
                    reimbursement_id,
                ),
            )

            row = cursor.fetchone()

            if row is None:

                raise LookupError(
                    "REIMBURSEMENT_NOT_FOUND"
                )

            if isinstance(
                row,
                dict,
            ):

                locked_raw = next(
                    iter(
                        row.values()
                    )
                )

            else:

                locked_raw = row[0]

            locked_row = (
                decode_json_object(
                    locked_raw
                )
            )

            current_status = (
                ReimbursementStatus(
                    str(
                        locked_row[
                            "status"
                        ]
                    )
                )
            )


            # ------------------------------------------------
            # Replay check occurs BEFORE state validation.
            #
            # This permits an exact retry to receive its
            # original response even if the reimbursement has
            # legitimately advanced afterwards.
            # ------------------------------------------------

            if idempotency is not None:

                cursor.execute(
                    f"""
                    SELECT
                        operation,
                        actor_id,
                        payload_fingerprint,
                        response_snapshot

                    FROM {REIMBURSEMENT_IDEMPOTENCY_TABLE}

                    WHERE
                        tenant_id = %s
                        AND
                        reimbursement_id = %s
                        AND
                        key_hash = %s

                    LIMIT 1
                    """,
                    (
                        tenant_id,
                        reimbursement_id,
                        idempotency.key_hash,
                    ),
                )

                replay_row = (
                    cursor.fetchone()
                )

                if replay_row is not None:

                    if isinstance(
                        replay_row,
                        dict,
                    ):

                        stored_operation = (
                            replay_row[
                                "operation"
                            ]
                        )

                        stored_actor_id = (
                            replay_row[
                                "actor_id"
                            ]
                        )

                        stored_fingerprint = (
                            replay_row[
                                "payload_fingerprint"
                            ]
                        )

                        stored_snapshot = (
                            replay_row[
                                "response_snapshot"
                            ]
                        )

                    else:

                        (
                            stored_operation,
                            stored_actor_id,
                            stored_fingerprint,
                            stored_snapshot,
                        ) = replay_row

                    assert_replay_compatible(
                        context=
                            idempotency,

                        stored_operation=
                            str(
                                stored_operation
                            ),

                        stored_actor_id=
                            str(
                                stored_actor_id
                            ),

                        stored_payload_fingerprint=
                            str(
                                stored_fingerprint
                            ),
                    )

                    return (
                        reimbursement_from_snapshot(
                            decode_json_object(
                                stored_snapshot
                            )
                        )
                    )


            initial_submission = (
                current_status
                ==
                ReimbursementStatus.DRAFT
                and
                target_status
                ==
                ReimbursementStatus.SUBMITTED
            )

            assert_transition(
                current_status=
                    current_status,

                target_status=
                    target_status,
            )

            audit_action = (
                audit_action_for_transition(
                    current_status=
                        current_status,

                    target_status=
                        target_status,
                )
            )

            audit_details = (
                _safe_details(
                    current_status=
                        current_status,

                    target_status=
                        target_status,

                    details=
                        details,
                )
            )


            cursor.execute(
                f"""
                UPDATE {REIMBURSEMENT_TABLE}

                SET
                    status = %s,

                    submitted_at =
                        CASE
                            WHEN %s
                            THEN COALESCE(
                                submitted_at,
                                NOW()
                            )
                            ELSE submitted_at
                        END,

                    updated_at = NOW()

                WHERE
                    tenant_id = %s
                    AND
                    reimbursement_id = %s

                RETURNING
                    submitted_at,
                    updated_at
                """,
                (
                    target_status.value,
                    initial_submission,
                    tenant_id,
                    reimbursement_id,
                ),
            )

            updated = (
                cursor.fetchone()
            )

            if updated is None:

                raise RuntimeError(
                    "REIMBURSEMENT_WORKFLOW_UPDATE_FAILED"
                )

            if isinstance(
                updated,
                dict,
            ):

                updated_submitted_at = (
                    updated[
                        "submitted_at"
                    ]
                )

                updated_at = (
                    updated[
                        "updated_at"
                    ]
                )

            else:

                (
                    updated_submitted_at,
                    updated_at,
                ) = updated


            response_snapshot = (
                database_row_snapshot(
                    locked_row
                )
            )

            response_snapshot[
                "status"
            ] = target_status.value

            response_snapshot[
                "submitted_at"
            ] = (
                updated_submitted_at
            )

            response_snapshot[
                "updated_at"
            ] = updated_at


            event = AuditEvent(
                tenant_id=
                    tenant_id,

                reimbursement_id=
                    reimbursement_id,

                action=
                    audit_action,

                actor_id=
                    actor_id,

                details=
                    audit_details,
            )

            cursor.execute(
                f"""
                INSERT INTO {REIMBURSEMENT_AUDIT_TABLE} (
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
                """,
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


            # ------------------------------------------------
            # Idempotency record is written in the SAME
            # transaction as status + audit.
            # ------------------------------------------------

            if idempotency is not None:

                cursor.execute(
                    f"""
                    INSERT INTO {REIMBURSEMENT_IDEMPOTENCY_TABLE} (
                        tenant_id,
                        reimbursement_id,
                        key_hash,
                        operation,
                        actor_id,
                        payload_fingerprint,
                        response_snapshot
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s::jsonb
                    )
                    """,
                    (
                        tenant_id,
                        reimbursement_id,
                        idempotency.key_hash,
                        idempotency.operation,
                        idempotency.actor_id,
                        idempotency.payload_fingerprint,

                        json.dumps(
                            response_snapshot,
                            ensure_ascii=False,
                            default=str,
                        ),
                    ),
                )

        finally:

            cursor.close()


    #
    # Idempotent calls return the exact transition snapshot,
    # not a later state that could race after COMMIT.
    #
    if (
        idempotency is not None
        and
        response_snapshot is not None
    ):

        return reimbursement_from_snapshot(
            response_snapshot
        )


    #
    # Preserve legacy behavior for callers that do not use an
    # idempotency key.
    #
    reimbursement = (
        repository.get(
            tenant_id=
                tenant_id,

            reimbursement_id=
                reimbursement_id,
        )
    )

    if reimbursement is None:

        raise RuntimeError(
            "REIMBURSEMENT_WORKFLOW_RELOAD_FAILED"
        )

    return reimbursement



def _persist_memory_atomic(
    *,
    repository: ReimbursementRepository,
    audit: ReimbursementAuditService,
    tenant_id: str,
    reimbursement_id: str,
    actor_id: str,
    target_status: ReimbursementStatus,
    details: dict[str, Any] | None,
    idempotency: IdempotencyContext | None,
) -> ReimbursementRequest:

    reimbursement = (
        repository.get(
            tenant_id=
                tenant_id,

            reimbursement_id=
                reimbursement_id,
        )
    )

    if reimbursement is None:

        raise LookupError(
            "REIMBURSEMENT_NOT_FOUND"
        )


    store = getattr(
        repository,
        "_reimbursement_idempotency_records",
        None,
    )

    if store is None:

        store = {}

        setattr(
            repository,
            "_reimbursement_idempotency_records",
            store,
        )


    idempotency_store_key = None

    if idempotency is not None:

        idempotency_store_key = (
            tenant_id,
            reimbursement_id,
            idempotency.key_hash,
        )

        stored = store.get(
            idempotency_store_key
        )

        if stored is not None:

            assert_replay_compatible(
                context=
                    idempotency,

                stored_operation=
                    stored[
                        "operation"
                    ],

                stored_actor_id=
                    stored[
                        "actor_id"
                    ],

                stored_payload_fingerprint=
                    stored[
                        "payload_fingerprint"
                    ],
            )

            return (
                reimbursement_from_snapshot(
                    stored[
                        "response_snapshot"
                    ]
                )
            )


    current_status = (
        reimbursement.status
    )

    previous_updated_at = (
        reimbursement.updated_at
    )

    previous_submitted_at = (
        reimbursement.submitted_at
    )

    initial_submission = (
        current_status
        ==
        ReimbursementStatus.DRAFT
        and
        target_status
        ==
        ReimbursementStatus.SUBMITTED
    )

    assert_transition(
        current_status=
            current_status,

        target_status=
            target_status,
    )

    audit_action = (
        audit_action_for_transition(
            current_status=
                current_status,

            target_status=
                target_status,
        )
    )

    audit_details = (
        _safe_details(
            current_status=
                current_status,

            target_status=
                target_status,

            details=
                details,
        )
    )


    try:

        if (
            initial_submission
            and
            reimbursement.submitted_at
            is None
        ):

            reimbursement.submitted_at = (
                utc_now()
            )

        transition_reimbursement(
            reimbursement=
                reimbursement,

            target_status=
                target_status,
        )

        repository.save(
            reimbursement
        )

        audit.record(
            tenant_id=
                tenant_id,

            reimbursement_id=
                reimbursement_id,

            action=
                audit_action,

            actor_id=
                actor_id,

            details=
                audit_details,
        )


        if (
            idempotency is not None
            and
            idempotency_store_key
            is not None
        ):

            store[
                idempotency_store_key
            ] = {
                "operation":
                    idempotency.operation,

                "actor_id":
                    idempotency.actor_id,

                "payload_fingerprint":
                    idempotency.payload_fingerprint,

                "response_snapshot":
                    reimbursement_snapshot(
                        reimbursement
                    ),
            }


    except Exception:

        reimbursement.status = (
            current_status
        )

        reimbursement.updated_at = (
            previous_updated_at
        )

        reimbursement.submitted_at = (
            previous_submitted_at
        )

        repository.save(
            reimbursement
        )

        raise


    #
    # Match PostgreSQL semantics:
    # an idempotent first execution returns a detached snapshot.
    #
    # This prevents a later legitimate transition from mutating
    # the Python object previously returned to the caller.
    #
    if (
        idempotency is not None
        and
        idempotency_store_key
        is not None
    ):

        stored_result = store.get(
            idempotency_store_key
        )

        if stored_result is None:

            raise RuntimeError(
                "IDEMPOTENCY_MEMORY_RECORD_MISSING"
            )

        return reimbursement_from_snapshot(
            stored_result[
                "response_snapshot"
            ]
        )

    return reimbursement



def persist_workflow_transition(
    *,
    repository: ReimbursementRepository,
    audit:
        ReimbursementAuditService
        |
        PostgresReimbursementAuditService,

    tenant_id: str,
    reimbursement_id: str,
    actor_id: str,
    target_status: ReimbursementStatus,
    details: dict[str, Any] | None = None,

    idempotency_key: str | None = None,
    idempotency_operation: str | None = None,
    idempotency_payload: Any = None,
) -> ReimbursementRequest:

    idempotency = (
        build_idempotency_context(
            idempotency_key=
                idempotency_key,

            operation=
                idempotency_operation,

            actor_id=
                actor_id,

            payload=
                (
                    details
                    if idempotency_payload
                    is None
                    else
                    idempotency_payload
                ),
        )
    )


    postgres_repository = isinstance(
        repository,
        PostgresReimbursementRepository,
    )

    postgres_audit = isinstance(
        audit,
        PostgresReimbursementAuditService,
    )


    if (
        postgres_repository
        and
        postgres_audit
    ):

        return _persist_postgres_atomic(
            repository=
                repository,

            tenant_id=
                tenant_id,

            reimbursement_id=
                reimbursement_id,

            actor_id=
                actor_id,

            target_status=
                target_status,

            details=
                details,

            idempotency=
                idempotency,
        )


    if (
        postgres_repository
        !=
        postgres_audit
    ):

        raise RuntimeError(
            "MIXED_WORKFLOW_PERSISTENCE_NOT_SUPPORTED"
        )


    return _persist_memory_atomic(
        repository=
            repository,

        audit=
            audit,

        tenant_id=
            tenant_id,

        reimbursement_id=
            reimbursement_id,

        actor_id=
            actor_id,

        target_status=
            target_status,

        details=
            details,

        idempotency=
            idempotency,
    )


def workflow_persistence_capabilities(
) -> dict:

    return {
        "version":
            WORKFLOW_PERSISTENCE_VERSION,

        "atomic_status_and_audit":
            True,

        "single_postgres_transaction":
            True,

        "row_lock":
            True,

        "rollback_on_failure":
            True,

        "server_derived_audit_action":
            True,

        "tenant_scoped":
            True,

        "transition_guards":
            True,

        "resubmission":
            True,

        "cancellation":
            True,

        "payment_pending":
            True,

        "paid":
            True,

        "human_review_required":
            True,

        "automatic_approval":
            False,

        "document_ai_deferred":
            True,

        "gemini_enabled":
            False,
    }
