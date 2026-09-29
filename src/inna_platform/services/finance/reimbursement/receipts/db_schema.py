from __future__ import annotations

from src.database.connection import (
    cursor_postgres,
)

from ..db_schema import (
    REIMBURSEMENT_TABLE,
)


RECEIPT_TABLE = (
    "inna_finance_reimbursement_receipts"
)


def ensure_receipt_schema() -> None:

    sql = f"""
    CREATE TABLE IF NOT EXISTS {RECEIPT_TABLE} (
        receipt_id TEXT PRIMARY KEY,

        tenant_id TEXT NOT NULL,

        reimbursement_id TEXT NOT NULL,

        uploaded_by_user_id TEXT NOT NULL,

        original_filename TEXT NOT NULL,

        safe_filename TEXT NOT NULL,

        mime_type TEXT NOT NULL
            CHECK (
                mime_type IN (
                    'application/pdf',
                    'image/png',
                    'image/jpeg'
                )
            ),

        size_bytes BIGINT NOT NULL
            CHECK (
                size_bytes > 0
                AND
                size_bytes <= 10485760
            ),

        sha256 CHAR(64) NOT NULL
            CHECK (
                sha256 ~ '^[0-9a-f]{{64}}$'
            ),

        storage_reference TEXT NOT NULL
            UNIQUE,

        untrusted_content BOOLEAN
            NOT NULL
            DEFAULT TRUE,

        validation_version TEXT
            NOT NULL,

        created_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        CONSTRAINT fk_reimbursement_receipt_request
            FOREIGN KEY (
                reimbursement_id
            )
            REFERENCES {REIMBURSEMENT_TABLE}
                (reimbursement_id)
            ON DELETE CASCADE,

        CONSTRAINT uq_reimbursement_receipt_hash
            UNIQUE (
                tenant_id,
                reimbursement_id,
                sha256
            )
    )
    """

    indexes = [
        f"""
        CREATE INDEX IF NOT EXISTS
            idx_reimbursement_receipts_lookup
        ON {RECEIPT_TABLE} (
            tenant_id,
            reimbursement_id,
            created_at DESC
        )
        """,

        f"""
        CREATE INDEX IF NOT EXISTS
            idx_reimbursement_receipts_uploader
        ON {RECEIPT_TABLE} (
            tenant_id,
            uploaded_by_user_id,
            created_at DESC
        )
        """,
    ]

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql
        )

        for index_sql in indexes:

            cursor.execute(
                index_sql
            )


def receipt_database_capabilities(
) -> dict:

    return {
        "version":
            "reimbursement-2a2",

        "persistent_receipt_metadata":
            True,

        "binary_outside_database":
            True,

        "supported_pdf":
            True,

        "supported_png":
            True,

        "supported_jpeg":
            True,

        "max_size_bytes":
            10485760,

        "sha256_integrity":
            True,

        "untrusted_document_content":
            True,

        "public_static_storage":
            False,

        "authenticated_upload_api":
            True,

        "owner_upload_only":
            True,

        "reviewer_metadata_access":
            True,

        "public_file_download":
            False,

        "gemini_enabled":
            False,
    }