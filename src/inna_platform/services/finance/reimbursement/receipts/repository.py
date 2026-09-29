from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.database.connection import (
    cursor_postgres,
)

from .db_schema import (
    RECEIPT_TABLE,
    ensure_receipt_schema,
)

from .models import (
    ReceiptRecord,
)


class ReceiptRepository(ABC):

    @abstractmethod
    def save(
        self,
        record: ReceiptRecord,
    ) -> ReceiptRecord:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ) -> ReceiptRecord | None:
        raise NotImplementedError

    @abstractmethod
    def list_for_reimbursement(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
    ) -> list[ReceiptRecord]:
        raise NotImplementedError


    @abstractmethod
    def delete(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ) -> bool:
        raise NotImplementedError


class InMemoryReceiptRepository(
    ReceiptRepository
):

    def __init__(self) -> None:

        self._items: dict[
            tuple[str, str],
            ReceiptRecord,
        ] = {}

    def save(
        self,
        record: ReceiptRecord,
    ) -> ReceiptRecord:

        self._items[
            (
                record.tenant_id,
                record.receipt_id,
            )
        ] = record

        return record

    def get(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ) -> ReceiptRecord | None:

        return self._items.get(
            (
                tenant_id,
                receipt_id,
            )
        )

    def list_for_reimbursement(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
    ) -> list[ReceiptRecord]:

        items = [
            item
            for (
                stored_tenant,
                _
            ),
            item
            in self._items.items()
            if (
                stored_tenant
                ==
                tenant_id

                and

                item.reimbursement_id
                ==
                reimbursement_id
            )
        ]

        items.sort(
            key=lambda item:
                item.created_at,
        )

        return items



    def delete(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ) -> bool:

        key = (
            tenant_id,
            receipt_id,
        )

        return (
            self._items.pop(
                key,
                None,
            )
            is not None
        )


def _from_row(
    row: dict[str, Any],
) -> ReceiptRecord:

    return ReceiptRecord(
        receipt_id=str(
            row["receipt_id"]
        ),

        tenant_id=str(
            row["tenant_id"]
        ),

        reimbursement_id=str(
            row[
                "reimbursement_id"
            ]
        ),

        uploaded_by_user_id=str(
            row[
                "uploaded_by_user_id"
            ]
        ),

        original_filename=str(
            row[
                "original_filename"
            ]
        ),

        safe_filename=str(
            row[
                "safe_filename"
            ]
        ),

        mime_type=str(
            row["mime_type"]
        ),

        size_bytes=int(
            row["size_bytes"]
        ),

        sha256=str(
            row["sha256"]
        ),

        storage_reference=str(
            row[
                "storage_reference"
            ]
        ),

        untrusted_content=bool(
            row[
                "untrusted_content"
            ]
        ),

        validation_version=str(
            row[
                "validation_version"
            ]
        ),

        created_at=
            row["created_at"],
    )


class PostgresReceiptRepository(
    ReceiptRepository
):

    def __init__(self) -> None:
        ensure_receipt_schema()

    def save(
        self,
        record: ReceiptRecord,
    ) -> ReceiptRecord:

        sql = f"""
        INSERT INTO {RECEIPT_TABLE} (
            receipt_id,
            tenant_id,
            reimbursement_id,
            uploaded_by_user_id,
            original_filename,
            safe_filename,
            mime_type,
            size_bytes,
            sha256,
            storage_reference,
            untrusted_content,
            validation_version,
            created_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """

        with cursor_postgres(
            dict_cursor=False,
            commit_automatico=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    record.receipt_id,
                    record.tenant_id,
                    record.reimbursement_id,
                    record.uploaded_by_user_id,
                    record.original_filename,
                    record.safe_filename,
                    record.mime_type,
                    record.size_bytes,
                    record.sha256,
                    record.storage_reference,
                    record.untrusted_content,
                    record.validation_version,
                    record.created_at,
                ),
            )

        return record

    def get(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ) -> ReceiptRecord | None:

        sql = f"""
        SELECT
            receipt_id,
            tenant_id,
            reimbursement_id,
            uploaded_by_user_id,
            original_filename,
            safe_filename,
            mime_type,
            size_bytes,
            sha256,
            storage_reference,
            untrusted_content,
            validation_version,
            created_at

        FROM {RECEIPT_TABLE}

        WHERE
            tenant_id = %s
            AND
            receipt_id = %s

        LIMIT 1
        """

        with cursor_postgres(
            dict_cursor=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    tenant_id,
                    receipt_id,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return _from_row(
            dict(row)
        )

    def list_for_reimbursement(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
    ) -> list[ReceiptRecord]:

        sql = f"""
        SELECT
            receipt_id,
            tenant_id,
            reimbursement_id,
            uploaded_by_user_id,
            original_filename,
            safe_filename,
            mime_type,
            size_bytes,
            sha256,
            storage_reference,
            untrusted_content,
            validation_version,
            created_at

        FROM {RECEIPT_TABLE}

        WHERE
            tenant_id = %s
            AND
            reimbursement_id = %s

        ORDER BY
            created_at ASC
        """

        with cursor_postgres(
            dict_cursor=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    tenant_id,
                    reimbursement_id,
                ),
            )

            rows = cursor.fetchall()

        return [
            _from_row(
                dict(row)
            )
            for row in rows
        ]


    def delete(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ) -> bool:

        sql = f"""
        DELETE FROM {RECEIPT_TABLE}

        WHERE
            tenant_id = %s
            AND
            receipt_id = %s

        RETURNING receipt_id
        """

        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    tenant_id,
                    receipt_id,
                ),
            )

            row = cursor.fetchone()

        return row is not None

