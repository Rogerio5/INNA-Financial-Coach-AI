from __future__ import annotations

import json

from abc import ABC, abstractmethod
from typing import Any

from src.database.connection import cursor_postgres

from .db_schema import (
    EXTRACTION_TABLE,
    ensure_extraction_schema,
)

from .models import (
    ReceiptExtractionRecord,
    ReceiptExtractionStatus,
)


class ReceiptExtractionRepository(ABC):

    @abstractmethod
    def save(
        self,
        record: ReceiptExtractionRecord,
    ) -> ReceiptExtractionRecord:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        *,
        tenant_id: str,
        extraction_id: str,
    ) -> ReceiptExtractionRecord | None:
        raise NotImplementedError

    @abstractmethod
    def list_for_receipt(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ) -> list[ReceiptExtractionRecord]:
        raise NotImplementedError

    @abstractmethod
    def latest_for_receipt(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ) -> ReceiptExtractionRecord | None:
        raise NotImplementedError


class InMemoryReceiptExtractionRepository(
    ReceiptExtractionRepository
):

    def __init__(self) -> None:

        self._items: dict[
            tuple[str, str],
            ReceiptExtractionRecord,
        ] = {}

    def save(
        self,
        record: ReceiptExtractionRecord,
    ) -> ReceiptExtractionRecord:

        duplicate = any(
            stored_extraction_id
            ==
            record.extraction_id

            for (
                _,
                stored_extraction_id,
            )
            in self._items.keys()
        )

        if duplicate:

            raise ValueError(
                "EXTRACTION_ALREADY_EXISTS"
            )

        self._items[
            (
                record.tenant_id,
                record.extraction_id,
            )
        ] = record

        return record

    def get(
        self,
        *,
        tenant_id: str,
        extraction_id: str,
    ) -> ReceiptExtractionRecord | None:

        return self._items.get(
            (
                tenant_id,
                extraction_id,
            )
        )

    def list_for_receipt(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ) -> list[ReceiptExtractionRecord]:

        items = [
            record
            for (
                stored_tenant,
                _
            ),
            record
            in self._items.items()
            if (
                stored_tenant == tenant_id
                and
                record.receipt_id == receipt_id
            )
        ]

        items.sort(
            key=lambda item:
                item.created_at
        )

        return items

    def latest_for_receipt(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ) -> ReceiptExtractionRecord | None:

        items = self.list_for_receipt(
            tenant_id=tenant_id,
            receipt_id=receipt_id,
        )

        if not items:
            return None

        return items[-1]


def _normalize_string_list(
    value: Any,
) -> list[str]:

    if value is None:
        return []

    if isinstance(
        value,
        str,
    ):

        try:
            value = json.loads(
                value
            )

        except json.JSONDecodeError:
            return [
                value
            ]

    if not isinstance(
        value,
        list,
    ):
        return []

    return [
        str(item)
        for item
        in value
    ]


def _from_row(
    row: dict[str, Any],
) -> ReceiptExtractionRecord:

    return ReceiptExtractionRecord(
        extraction_id=str(
            row["extraction_id"]
        ),

        tenant_id=str(
            row["tenant_id"]
        ),

        reimbursement_id=str(
            row["reimbursement_id"]
        ),

        receipt_id=str(
            row["receipt_id"]
        ),

        merchant_name=
            row.get("merchant_name"),

        merchant_tax_id=
            row.get("merchant_tax_id"),

        document_number=
            row.get("document_number"),

        expense_date=
            row.get("expense_date"),

        expense_time=
            row.get("expense_time"),

        currency=
            row.get("currency"),

        subtotal_minor=(
            int(row["subtotal_minor"])
            if row.get("subtotal_minor") is not None
            else None
        ),

        tax_minor=(
            int(row["tax_minor"])
            if row.get("tax_minor") is not None
            else None
        ),

        total_minor=(
            int(row["total_minor"])
            if row.get("total_minor") is not None
            else None
        ),

        payment_method=
            row.get("payment_method"),

        confidence=float(
            row.get(
                "confidence",
                0,
            )
        ),

        warnings=
            _normalize_string_list(
                row.get("warnings")
            ),

        inconsistencies=
            _normalize_string_list(
                row.get(
                    "inconsistencies"
                )
            ),

        extraction_status=
            ReceiptExtractionStatus(
                row["extraction_status"]
            ),

        extractor=str(
            row["extractor"]
        ),

        extractor_version=str(
            row["extractor_version"]
        ),

        document_content_trusted=bool(
            row["document_content_trusted"]
        ),

        human_review_required=bool(
            row["human_review_required"]
        ),

        created_at=
            row["created_at"],

        updated_at=
            row["updated_at"],
    )


class PostgresReceiptExtractionRepository(
    ReceiptExtractionRepository
):

    def __init__(self) -> None:
        ensure_extraction_schema()

    def save(
        self,
        record: ReceiptExtractionRecord,
    ) -> ReceiptExtractionRecord:

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

        with cursor_postgres(
            dict_cursor=False,
            commit_automatico=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    record.extraction_id,
                    record.tenant_id,
                    record.reimbursement_id,
                    record.receipt_id,

                    record.merchant_name,
                    record.merchant_tax_id,
                    record.document_number,

                    record.expense_date,
                    record.expense_time,

                    record.currency,

                    record.subtotal_minor,
                    record.tax_minor,
                    record.total_minor,

                    record.payment_method,
                    record.confidence,

                    json.dumps(
                        record.warnings,
                        ensure_ascii=False,
                    ),

                    json.dumps(
                        record.inconsistencies,
                        ensure_ascii=False,
                    ),

                    record.extraction_status.value,

                    record.extractor,
                    record.extractor_version,

                    record.document_content_trusted,
                    record.human_review_required,

                    record.created_at,
                    record.updated_at,
                ),
            )

        return record

    def get(
        self,
        *,
        tenant_id: str,
        extraction_id: str,
    ) -> ReceiptExtractionRecord | None:

        sql = f"""
        SELECT *
        FROM {EXTRACTION_TABLE}

        WHERE
            tenant_id = %s
            AND
            extraction_id = %s

        LIMIT 1
        """

        with cursor_postgres(
            dict_cursor=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    tenant_id,
                    extraction_id,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return _from_row(
            dict(row)
        )

    def list_for_receipt(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ) -> list[ReceiptExtractionRecord]:

        sql = f"""
        SELECT *
        FROM {EXTRACTION_TABLE}

        WHERE
            tenant_id = %s
            AND
            receipt_id = %s

        ORDER BY
            created_at ASC,
            extraction_id ASC
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

            rows = cursor.fetchall()

        return [
            _from_row(
                dict(row)
            )
            for row
            in rows
        ]

    def latest_for_receipt(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ) -> ReceiptExtractionRecord | None:

        sql = f"""
        SELECT *
        FROM {EXTRACTION_TABLE}

        WHERE
            tenant_id = %s
            AND
            receipt_id = %s

        ORDER BY
            created_at DESC,
            extraction_id DESC

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
