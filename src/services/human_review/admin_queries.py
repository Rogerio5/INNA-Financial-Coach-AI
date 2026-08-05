from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from src.database.connection import (
    cursor_postgres,
)

from .admin_contracts import (
    HumanReviewAdminFilters,
    HumanReviewAdminMetrics,
    HumanReviewAdminPage,
)
from .exceptions import (
    HumanReviewRepositoryError,
)


BASE_ADMIN_SELECT = """
SELECT
    id,
    review_id,
    thread_id,
    status,
    requested_by,
    reason,
    trigger,
    risk_level,
    payload,
    allowed_actions,
    decision_action,
    reviewer_id,
    reviewer_comment,
    rejection_reason,
    corrections,
    resume_route,
    processing_request_id,
    processing_started_at,
    failure_reason,
    created_at,
    updated_at,
    resolved_at
FROM public.human_reviews
"""


def _normalize_row(
    row: Mapping[str, Any],
) -> dict[str, Any]:
    result = dict(row)

    for key in (
        "created_at",
        "updated_at",
        "resolved_at",
        "processing_started_at",
    ):
        value = result.get(key)

        if isinstance(value, datetime):
            result[key] = value.isoformat()

    result["payload"] = dict(result.get("payload") or {})

    result["corrections"] = dict(result.get("corrections") or {})

    result["allowed_actions"] = list(result.get("allowed_actions") or [])

    return result


def _build_where(
    filters: HumanReviewAdminFilters,
) -> tuple[str, dict[str, Any]]:
    conditions: list[str] = []
    parameters: dict[str, Any] = {}

    if filters.statuses:
        conditions.append("status = ANY(%(statuses)s)")
        parameters["statuses"] = list(filters.statuses)

    if filters.risk_levels:
        conditions.append("risk_level = ANY(%(risk_levels)s)")
        parameters["risk_levels"] = list(filters.risk_levels)

    if filters.requested_by:
        conditions.append("requested_by = %(requested_by)s")
        parameters["requested_by"] = filters.requested_by

    if filters.reviewer_id:
        conditions.append("reviewer_id = %(reviewer_id)s")
        parameters["reviewer_id"] = filters.reviewer_id

    if filters.thread_id:
        conditions.append("thread_id = %(thread_id)s")
        parameters["thread_id"] = filters.thread_id

    if filters.created_from is not None:
        conditions.append("created_at >= %(created_from)s")
        parameters["created_from"] = filters.created_from

    if filters.created_to is not None:
        conditions.append("created_at <= %(created_to)s")
        parameters["created_to"] = filters.created_to

    if filters.search:
        conditions.append("""
            (
                review_id ILIKE %(search)s
                OR thread_id ILIKE %(search)s
                OR reason ILIKE %(search)s
                OR trigger ILIKE %(search)s
                OR requested_by ILIKE %(search)s
                OR reviewer_id ILIKE %(search)s
            )
        """)

        parameters["search"] = f"%{filters.search}%"

    if not conditions:
        return "", parameters

    return (
        " WHERE " + " AND ".join(conditions),
        parameters,
    )


def listar_revisoes_admin(
    filters: HumanReviewAdminFilters,
) -> HumanReviewAdminPage:
    if not isinstance(
        filters,
        HumanReviewAdminFilters,
    ):
        raise TypeError("filters deve ser HumanReviewAdminFilters.")

    where_sql, parameters = _build_where(filters)

    count_sql = "SELECT COUNT(*) AS total FROM public.human_reviews" + where_sql

    list_sql = (
        BASE_ADMIN_SELECT
        + where_sql
        + """
        ORDER BY
            CASE status
                WHEN 'processing' THEN 1
                WHEN 'pending' THEN 2
                WHEN 'resume_failed' THEN 3
                ELSE 4
            END,
            created_at ASC,
            id ASC
        LIMIT %(limit)s
        OFFSET %(offset)s
        """
    )

    list_parameters = {
        **parameters,
        "limit": filters.limit,
        "offset": filters.offset,
    }

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=False,
        ) as cursor:
            cursor.execute(
                count_sql,
                parameters,
            )

            count_row = cursor.fetchone()

            cursor.execute(
                list_sql,
                list_parameters,
            )

            rows = cursor.fetchall()

    except Exception as exc:
        raise HumanReviewRepositoryError(
            "Não foi possível listar as revisões administrativas."
        ) from exc

    total = int(count_row["total"] if count_row else 0)

    return HumanReviewAdminPage(
        items=[_normalize_row(row) for row in rows],
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


def obter_metricas_admin(
    *,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
) -> HumanReviewAdminMetrics:
    filters = HumanReviewAdminFilters(
        created_from=created_from,
        created_to=created_to,
    )

    where_sql, parameters = _build_where(filters)

    summary_sql = (
        """
    SELECT
        COUNT(*) AS total,
        COUNT(*) FILTER (
            WHERE status = 'pending'
        ) AS pending,
        COUNT(*) FILTER (
            WHERE status = 'processing'
        ) AS processing,
        COUNT(*) FILTER (
            WHERE status = 'approved'
        ) AS approved,
        COUNT(*) FILTER (
            WHERE status = 'corrected'
        ) AS corrected,
        COUNT(*) FILTER (
            WHERE status = 'rejected'
        ) AS rejected,
        COUNT(*) FILTER (
            WHERE status = 'cancelled'
        ) AS cancelled,
        COUNT(*) FILTER (
            WHERE status = 'resume_failed'
        ) AS resume_failed,
        AVG(
            EXTRACT(
                EPOCH FROM (
                    processing_started_at
                    - created_at
                )
            )
        ) FILTER (
            WHERE processing_started_at
                IS NOT NULL
        ) AS average_wait_seconds,
        AVG(
            EXTRACT(
                EPOCH FROM (
                    resolved_at
                    - created_at
                )
            )
        ) FILTER (
            WHERE resolved_at IS NOT NULL
        ) AS average_resolution_seconds
    FROM public.human_reviews
    """
        + where_sql
    )

    risk_sql = (
        """
    SELECT
        COALESCE(
            NULLIF(risk_level, ''),
            'unknown'
        ) AS dimension,
        COUNT(*) AS total
    FROM public.human_reviews
    """
        + where_sql
        + """
    GROUP BY 1
    ORDER BY total DESC, dimension ASC
    """
    )

    agent_sql = (
        """
    SELECT
        COALESCE(
            NULLIF(requested_by, ''),
            'unknown'
        ) AS dimension,
        COUNT(*) AS total
    FROM public.human_reviews
    """
        + where_sql
        + """
    GROUP BY 1
    ORDER BY total DESC, dimension ASC
    LIMIT 20
    """
    )

    reviewer_sql = (
        """
    SELECT
        COALESCE(
            NULLIF(reviewer_id, ''),
            'unassigned'
        ) AS dimension,
        COUNT(*) AS total
    FROM public.human_reviews
    """
        + where_sql
        + """
    GROUP BY 1
    ORDER BY total DESC, dimension ASC
    LIMIT 20
    """
    )

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=False,
        ) as cursor:
            cursor.execute(
                summary_sql,
                parameters,
            )
            summary = cursor.fetchone() or {}

            cursor.execute(
                risk_sql,
                parameters,
            )
            risks = cursor.fetchall()

            cursor.execute(
                agent_sql,
                parameters,
            )
            agents = cursor.fetchall()

            cursor.execute(
                reviewer_sql,
                parameters,
            )
            reviewers = cursor.fetchall()

    except Exception as exc:
        raise HumanReviewRepositoryError(
            "Não foi possível calcular as métricas administrativas."
        ) from exc

    total = int(summary.get("total") or 0)

    approved = int(summary.get("approved") or 0)

    corrected = int(summary.get("corrected") or 0)

    terminal_total = sum(
        [
            approved,
            corrected,
            int(summary.get("rejected") or 0),
            int(summary.get("cancelled") or 0),
        ]
    )

    def rate(value: int) -> float:
        if terminal_total == 0:
            return 0.0

        return round(
            value / terminal_total,
            4,
        )

    def dimension_map(
        rows: list[Mapping[str, Any]],
    ) -> dict[str, int]:
        return {str(row["dimension"]): int(row["total"]) for row in rows}

    return HumanReviewAdminMetrics(
        total=total,
        pending=int(summary.get("pending") or 0),
        processing=int(summary.get("processing") or 0),
        approved=approved,
        corrected=corrected,
        rejected=int(summary.get("rejected") or 0),
        cancelled=int(summary.get("cancelled") or 0),
        resume_failed=int(summary.get("resume_failed") or 0),
        average_wait_seconds=(
            float(summary["average_wait_seconds"])
            if summary.get("average_wait_seconds") is not None
            else None
        ),
        average_resolution_seconds=(
            float(summary["average_resolution_seconds"])
            if summary.get("average_resolution_seconds") is not None
            else None
        ),
        approval_rate=rate(approved),
        correction_rate=rate(corrected),
        by_risk=dimension_map(risks),
        by_agent=dimension_map(agents),
        by_reviewer=dimension_map(reviewers),
    )


__all__ = [
    "listar_revisoes_admin",
    "obter_metricas_admin",
]
