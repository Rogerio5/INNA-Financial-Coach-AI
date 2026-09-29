from __future__ import annotations

from src.database.connection import cursor_postgres

from ..db_schema import (
    RECEIPT_TABLE,
    ensure_receipt_schema,
)


EXTRACTION_TABLE = (
    "inna_finance_reimbursement_receipt_extractions"
)


def ensure_extraction_schema() -> None:

    ensure_receipt_schema()

    sql = f"""
    CREATE TABLE IF NOT EXISTS {EXTRACTION_TABLE} (

        extraction_id TEXT PRIMARY KEY,

        tenant_id TEXT NOT NULL,
        reimbursement_id TEXT NOT NULL,
        receipt_id TEXT NOT NULL,

        merchant_name TEXT NULL,
        merchant_tax_id TEXT NULL,
        document_number TEXT NULL,

        expense_date DATE NULL,
        expense_time TIME NULL,

        currency VARCHAR(3) NULL
            CHECK (
                currency IS NULL
                OR (
                    CHAR_LENGTH(currency) = 3
                    AND
                    currency = UPPER(currency)
                )
            ),

        subtotal_minor BIGINT NULL
            CHECK (
                subtotal_minor IS NULL
                OR subtotal_minor >= 0
            ),

        tax_minor BIGINT NULL
            CHECK (
                tax_minor IS NULL
                OR tax_minor >= 0
            ),

        total_minor BIGINT NULL
            CHECK (
                total_minor IS NULL
                OR total_minor >= 0
            ),

        payment_method TEXT NULL,

        confidence NUMERIC(5,4)
            NOT NULL
            DEFAULT 0
            CHECK (
                confidence >= 0
                AND
                confidence <= 1
            ),

        warnings JSONB
            NOT NULL
            DEFAULT '[]'::jsonb,

        inconsistencies JSONB
            NOT NULL
            DEFAULT '[]'::jsonb,

        extraction_status TEXT
            NOT NULL
            CHECK (
                extraction_status IN (
                    'pending',
                    'extracted',
                    'needs_review',
                    'failed'
                )
            ),

        extractor TEXT NOT NULL,
        extractor_version TEXT NOT NULL,

        document_content_trusted BOOLEAN
            NOT NULL
            DEFAULT FALSE
            CHECK (
                document_content_trusted = FALSE
            ),

        human_review_required BOOLEAN
            NOT NULL
            DEFAULT TRUE
            CHECK (
                human_review_required = TRUE
            ),

        created_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        updated_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        CONSTRAINT fk_receipt_extraction_receipt
            FOREIGN KEY (receipt_id)
            REFERENCES {RECEIPT_TABLE}(receipt_id)
            ON DELETE CASCADE
    )
    """

    indexes = [
        f"""
        CREATE INDEX IF NOT EXISTS
            idx_receipt_extraction_receipt
        ON {EXTRACTION_TABLE} (
            tenant_id,
            receipt_id,
            created_at DESC
        )
        """,

        f"""
        CREATE INDEX IF NOT EXISTS
            idx_receipt_extraction_reimbursement
        ON {EXTRACTION_TABLE} (
            tenant_id,
            reimbursement_id,
            created_at DESC
        )
        """,

        f"""
        CREATE INDEX IF NOT EXISTS
            idx_receipt_extraction_status
        ON {EXTRACTION_TABLE} (
            tenant_id,
            extraction_status,
            created_at DESC
        )
        """,
    ]

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(sql)

        for index_sql in indexes:
            cursor.execute(
                index_sql
            )


def extraction_capabilities() -> dict:

    return {
        "version":
            "reimbursement-2b6",

        "structured_extraction_contract":
            True,

        "persistent_extraction":
            True,

        "tenant_scoped":
            True,

        "receipt_scoped":
            True,

        "money_minor_units":
            True,

        "structured_validation":
            True,

        "document_content_trusted":
            False,

        "human_review_required":
            True,

        "automatic_approval":
            False,

        "local_pdf_extraction_enabled":
            True,

        "reimbursement_comparison":
            True,

        "amount_comparison":
            True,

        "currency_comparison":
            True,

        "date_comparison":
            True,

        "merchant_comparison":
            True,

        "validation_metadata_bridge":
            True,

        "authenticated_extraction_api":
            True,

        "analysis_metadata_consumption":
            True,

        "extraction_audit":
            True,

        "append_only_extraction":
            True,

        "atomic_extraction_persistence":
            True,

        "single_transaction_postgres":
            True,

        "rollback_on_atomic_failure":
            True,

        "image_vision_enabled":
            False,

        "gemini_enabled":
            False,
    }