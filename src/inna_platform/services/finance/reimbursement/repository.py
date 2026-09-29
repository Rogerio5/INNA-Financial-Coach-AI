from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any

from src.database.connection import cursor_postgres

from .db_schema import REIMBURSEMENT_TABLE
from .models import (
    ReimbursementRequest,
    ReimbursementStatus,
)


class ReimbursementRepository(ABC):

    @abstractmethod
    def save(
        self,
        reimbursement: ReimbursementRequest,
    ) -> ReimbursementRequest:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
    ) -> ReimbursementRequest | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_user(
        self,
        *,
        tenant_id: str,
        user_id: str,
    ) -> list[ReimbursementRequest]:
        raise NotImplementedError


class InMemoryReimbursementRepository(
    ReimbursementRepository
):

    def __init__(self) -> None:
        self._items: dict[
            tuple[str, str],
            ReimbursementRequest,
        ] = {}

    def save(
        self,
        reimbursement: ReimbursementRequest,
    ) -> ReimbursementRequest:

        key = (
            reimbursement.tenant_id,
            reimbursement.id,
        )

        self._items[key] = reimbursement

        return reimbursement

    def get(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
    ) -> ReimbursementRequest | None:

        return self._items.get(
            (
                tenant_id,
                reimbursement_id,
            )
        )

    def list_by_user(
        self,
        *,
        tenant_id: str,
        user_id: str,
    ) -> list[ReimbursementRequest]:

        return [
            item
            for (
                stored_tenant,
                _
            ),
            item
            in self._items.items()
            if (
                stored_tenant == tenant_id
                and
                item.user_id == user_id
            )
        ]



    def list_by_tenant(
        self,
        *,
        tenant_id: str,
        status: ReimbursementStatus | None = None,
        limit: int = 100,
    ) -> list[ReimbursementRequest]:

        safe_limit = max(
            1,
            min(
                int(limit),
                500,
            ),
        )

        items = [
            item
            for (
                stored_tenant,
                _
            ),
            item
            in self._items.items()
            if stored_tenant == tenant_id
        ]

        if status is not None:

            items = [
                item
                for item
                in items
                if item.status == status
            ]

        items.sort(
            key=lambda item:
                item.created_at,
            reverse=True,
        )

        return items[
            :safe_limit
        ]


def _normalize_json(
    value: Any,
) -> dict[str, Any]:

    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if isinstance(value, str):
        try:
            parsed = json.loads(value)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            return {}

    return {}


def _date_to_text(
    value: Any,
) -> str | None:

    if value is None:
        return None

    if isinstance(
        value,
        (date, datetime),
    ):
        return value.isoformat()[:10]

    return str(value)


def _row_to_request(
    row: dict[str, Any],
) -> ReimbursementRequest:

    return ReimbursementRequest(
        id=str(
            row["reimbursement_id"]
        ),

        tenant_id=str(
            row["tenant_id"]
        ),

        user_id=str(
            row["user_id"]
        ),

        amount=int(
            row["amount_minor"]
        ),

        currency=str(
            row["currency"]
        ),

        category=str(
            row["category"]
        ),

        description=str(
            row["description"]
        ),

        merchant=row.get(
            "merchant"
        ),

        expense_date=_date_to_text(
            row.get(
                "expense_date"
            )
        ),

        receipt_reference=row.get(
            "receipt_reference"
        ),

        source_type=str(
            row.get(
                "source_type"
            )
            or
            "finance"
        ),

        source_reference=row.get(
            "source_reference"
        ),

        status=ReimbursementStatus(
            row["status"]
        ),

        requires_human_review=bool(
            row.get(
                "requires_human_review",
                True,
            )
        ),

        metadata=_normalize_json(
            row.get(
                "metadata"
            )
        ),

        submitted_at=row.get("submitted_at"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class PostgresReimbursementRepository(
    ReimbursementRepository
):

    def save(
        self,
        reimbursement: ReimbursementRequest,
    ) -> ReimbursementRequest:

        sql = f"""
        INSERT INTO {REIMBURSEMENT_TABLE} (
            reimbursement_id,
            tenant_id,
            user_id,
            amount_minor,
            currency,
            category,
            description,
            merchant,
            expense_date,
            receipt_reference,
            source_type,
            source_reference,
            status,
            requires_human_review,
            metadata,
            submitted_at,
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
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s::jsonb,
            %s,
            %s,
            %s
        )

        ON CONFLICT (
            reimbursement_id
        )
        DO UPDATE SET
            tenant_id =
                EXCLUDED.tenant_id,

            user_id =
                EXCLUDED.user_id,

            amount_minor =
                EXCLUDED.amount_minor,

            currency =
                EXCLUDED.currency,

            category =
                EXCLUDED.category,

            description =
                EXCLUDED.description,

            merchant =
                EXCLUDED.merchant,

            expense_date =
                EXCLUDED.expense_date,

            receipt_reference =
                EXCLUDED.receipt_reference,

            source_type =
                EXCLUDED.source_type,

            source_reference =
                EXCLUDED.source_reference,

            status =
                EXCLUDED.status,

            requires_human_review =
                EXCLUDED.requires_human_review,

            metadata =
                EXCLUDED.metadata,

            submitted_at =
                COALESCE(
                    {REIMBURSEMENT_TABLE}.submitted_at,
                    EXCLUDED.submitted_at
                ),

            updated_at =
                EXCLUDED.updated_at

        RETURNING *
        """

        metadata_json = json.dumps(
            reimbursement.metadata,
            ensure_ascii=False,
            default=str,
        )

        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    reimbursement.id,
                    reimbursement.tenant_id,
                    reimbursement.user_id,
                    reimbursement.amount,
                    reimbursement.currency,
                    reimbursement.category,
                    reimbursement.description,
                    reimbursement.merchant,
                    reimbursement.expense_date,
                    reimbursement.receipt_reference,
                    reimbursement.source_type,
                    reimbursement.source_reference,
                    reimbursement.status.value,
                    reimbursement.requires_human_review,
                    metadata_json,
                    reimbursement.submitted_at,
                    reimbursement.created_at,
                    reimbursement.updated_at,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "REIMBURSEMENT_SAVE_FAILED"
            )

        return _row_to_request(
            dict(row)
        )

    def get(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
    ) -> ReimbursementRequest | None:

        sql = f"""
        SELECT *
        FROM {REIMBURSEMENT_TABLE}

        WHERE
            tenant_id = %s
            AND
            reimbursement_id = %s

        LIMIT 1
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

            row = cursor.fetchone()

        if row is None:
            return None

        return _row_to_request(
            dict(row)
        )

    def list_by_user(
        self,
        *,
        tenant_id: str,
        user_id: str,
    ) -> list[ReimbursementRequest]:

        sql = f"""
        SELECT *
        FROM {REIMBURSEMENT_TABLE}

        WHERE
            tenant_id = %s
            AND
            user_id = %s

        ORDER BY
            created_at DESC
        """

        with cursor_postgres(
            dict_cursor=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    tenant_id,
                    user_id,
                ),
            )

            rows = cursor.fetchall()

        return [
            _row_to_request(
                dict(row)
            )
            for row in rows
        ]

    def list_by_tenant(
        self,
        *,
        tenant_id: str,
        status: ReimbursementStatus | None = None,
        limit: int = 100,
    ) -> list[ReimbursementRequest]:

        safe_limit = max(
            1,
            min(
                int(limit),
                500,
            ),
        )

        if status is None:

            sql = f"""
            SELECT *
            FROM {REIMBURSEMENT_TABLE}

            WHERE
                tenant_id = %s

            ORDER BY
                created_at DESC

            LIMIT %s
            """

            params = (
                tenant_id,
                safe_limit,
            )

        else:

            sql = f"""
            SELECT *
            FROM {REIMBURSEMENT_TABLE}

            WHERE
                tenant_id = %s
                AND
                status = %s

            ORDER BY
                created_at DESC

            LIMIT %s
            """

            params = (
                tenant_id,
                status.value,
                safe_limit,
            )

        with cursor_postgres(
            dict_cursor=True,
        ) as cursor:

            cursor.execute(
                sql,
                params,
            )

            rows = cursor.fetchall()

        return [
            _row_to_request(
                dict(row)
            )
            for row in rows
        ]