from __future__ import annotations

import json

from typing import Any

from src.database.connection import (
    conexao_postgres,
)

from ...audit.audit_service import (
    AuditEvent,
    PostgresReimbursementAuditService,
    ReimbursementAuditService,
)

from ...db_schema import (
    REIMBURSEMENT_AUDIT_TABLE,
    REIMBURSEMENT_TABLE,
)

from ...models import (
    ReimbursementRequest,
)

from ...repository import (
    PostgresReimbursementRepository,
    ReimbursementRepository,
)

from .db_schema import (
    EXTRACTION_TABLE,
)

from .models import (
    ReceiptExtractionRecord,
)

from .repository import (
    PostgresReceiptExtractionRepository,
    ReceiptExtractionRepository,
)


def build_extraction_audit_details(
    extraction: ReceiptExtractionRecord,
) -> dict[str, Any]:

    return {
        "receipt_id":
            extraction.receipt_id,

        "extraction_id":
            extraction.extraction_id,

        "extraction_status":
            extraction.extraction_status.value,

        "extractor":
            extraction.extractor,

        "extractor_version":
            extraction.extractor_version,

        "confidence":
            extraction.confidence,

        "warning_count":
            len(
                extraction.warnings
            ),

        "inconsistency_count":
            len(
                extraction.inconsistencies
            ),

        "inconsistencies":
            list(
                extraction.inconsistencies
            ),

        "document_content_trusted":
            False,

        "human_review_required":
            True,

        "automatic_approval":
            False,
    }


def _insert_extraction(
    *,
    cursor,
    extraction: ReceiptExtractionRecord,
) -> None:

    sql = f"""
    INSERT INTO {EXTRACTION_TABLE} (
        extraction_id,
        tenant_id,
        reimbursement_id,
        receipt_id,

        merchant_name,
        merchant_tax_id,
        document_number,

        expense_date,
        expense_time,

        currency,

        subtotal_minor,
        tax_minor,
        total_minor,

        payment_method,
        confidence,

        warnings,
        inconsistencies,

        extraction_status,

        extractor,
        extractor_version,

        document_content_trusted,
        human_review_required,

        created_at,
        updated_at
    )
    VALUES (
        %s, %s, %s, %s,
        %s, %s, %s,
        %s, %s,
        %s,
        %s, %s, %s,
        %s,
        %s,
        %s::jsonb,
        %s::jsonb,
        %s,
        %s, %s,
        %s, %s,
        %s, %s
    )
    """

    cursor.execute(
        sql,
        (
            extraction.extraction_id,
            extraction.tenant_id,
            extraction.reimbursement_id,
            extraction.receipt_id,

            extraction.merchant_name,
            extraction.merchant_tax_id,
            extraction.document_number,

            extraction.expense_date,
            extraction.expense_time,

            extraction.currency,

            extraction.subtotal_minor,
            extraction.tax_minor,
            extraction.total_minor,

            extraction.payment_method,
            extraction.confidence,

            json.dumps(
                extraction.warnings,
                ensure_ascii=False,
            ),

            json.dumps(
                extraction.inconsistencies,
                ensure_ascii=False,
            ),

            extraction.extraction_status.value,

            extraction.extractor,
            extraction.extractor_version,

            extraction.document_content_trusted,
            extraction.human_review_required,

            extraction.created_at,
            extraction.updated_at,
        ),
    )


def _update_reimbursement_validation(
    *,
    cursor,
    reimbursement: ReimbursementRequest,
) -> None:

    validation = (
        reimbursement.metadata.get(
            "receipt_validation"
        )
    )

    if not isinstance(
        validation,
        dict,
    ):

        raise RuntimeError(
            "RECEIPT_VALIDATION_METADATA_REQUIRED"
        )

    patch_json = json.dumps(
        {
            "receipt_validation":
                validation,
        },
        ensure_ascii=False,
        default=str,
    )

    sql = f"""
    UPDATE {REIMBURSEMENT_TABLE}

    SET
        metadata =
            COALESCE(
                metadata,
                '{{}}'::jsonb
            )
            ||
            %s::jsonb,

        updated_at = %s

    WHERE
        tenant_id = %s
        AND
        reimbursement_id = %s
    """

    cursor.execute(
        sql,
        (
            patch_json,
            reimbursement.updated_at,
            reimbursement.tenant_id,
            reimbursement.id,
        ),
    )

    if cursor.rowcount != 1:

        raise RuntimeError(
            "REIMBURSEMENT_ATOMIC_UPDATE_FAILED"
        )


def _insert_audit(
    *,
    cursor,
    event: AuditEvent,
) -> None:

    details_json = json.dumps(
        event.details,
        ensure_ascii=False,
        default=str,
    )

    sql = f"""
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
    """

    cursor.execute(
        sql,
        (
            event.event_id,
            event.tenant_id,
            event.reimbursement_id,
            event.action,
            event.actor_id,
            details_json,
            event.created_at,
        ),
    )


def _persist_postgres_atomic(
    *,
    reimbursement: ReimbursementRequest,
    extraction: ReceiptExtractionRecord,
    actor_id: str,
) -> AuditEvent:

    if (
        extraction.tenant_id
        !=
        reimbursement.tenant_id
    ):

        raise ValueError(
            "ATOMIC_TENANT_MISMATCH"
        )

    if (
        extraction.reimbursement_id
        !=
        reimbursement.id
    ):

        raise ValueError(
            "ATOMIC_REIMBURSEMENT_MISMATCH"
        )

    event = AuditEvent(
        tenant_id=
            reimbursement.tenant_id,

        reimbursement_id=
            reimbursement.id,

        action=
            "reimbursement.receipt.extracted",

        actor_id=
            actor_id,

        details=
            build_extraction_audit_details(
                extraction
            ),
    )

    #
    # One physical PostgreSQL connection.
    # conexao_postgres commits only on successful exit.
    # Any exception propagates through the context manager,
    # which performs rollback.
    #
    with conexao_postgres(
        autocommit=False,
        commit_automatico=True,
    ) as connection:

        cursor = connection.cursor()

        try:

            _insert_extraction(
                cursor=cursor,
                extraction=extraction,
            )

            _update_reimbursement_validation(
                cursor=cursor,
                reimbursement=reimbursement,
            )

            _insert_audit(
                cursor=cursor,
                event=event,
            )

        finally:

            cursor.close()

    return event


def persist_validated_extraction(
    *,
    extraction_repository:
        ReceiptExtractionRepository,

    reimbursement_repository:
        ReimbursementRepository,

    audit:
        ReimbursementAuditService
        |
        PostgresReimbursementAuditService,

    reimbursement:
        ReimbursementRequest,

    extraction:
        ReceiptExtractionRecord,

    actor_id:
        str,
) -> AuditEvent:

    postgres_components = (
        isinstance(
            extraction_repository,
            PostgresReceiptExtractionRepository,
        ),
        isinstance(
            reimbursement_repository,
            PostgresReimbursementRepository,
        ),
        isinstance(
            audit,
            PostgresReimbursementAuditService,
        ),
    )

    if all(
        postgres_components
    ):

        return _persist_postgres_atomic(
            reimbursement=
                reimbursement,

            extraction=
                extraction,

            actor_id=
                actor_id,
        )

    if any(
        postgres_components
    ):

        raise RuntimeError(
            "MIXED_REIMBURSEMENT_PERSISTENCE_NOT_SUPPORTED"
        )

    #
    # Test/in-memory runtime.
    # Production runtime above uses one PostgreSQL transaction.
    #
    extraction_repository.save(
        extraction
    )

    reimbursement_repository.save(
        reimbursement
    )

    return audit.record(
        tenant_id=
            reimbursement.tenant_id,

        reimbursement_id=
            reimbursement.id,

        action=
            "reimbursement.receipt.extracted",

        actor_id=
            actor_id,

        details=
            build_extraction_audit_details(
                extraction
            ),
    )
