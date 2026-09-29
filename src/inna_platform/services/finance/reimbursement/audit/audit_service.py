from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.database.connection import cursor_postgres

from ..db_schema import (
    REIMBURSEMENT_AUDIT_TABLE,
)


def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


@dataclass(frozen=True)
class AuditEvent:
    tenant_id: str
    reimbursement_id: str
    action: str
    actor_id: str

    event_id: str = field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    details: dict[str, Any] = field(
        default_factory=dict
    )

    created_at: datetime = field(
        default_factory=utc_now
    )


class ReimbursementAuditService:
    """
    In-memory audit used by unit tests.
    """

    def __init__(self) -> None:
        self._events: list[
            AuditEvent
        ] = []

    def record(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
        action: str,
        actor_id: str,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:

        event = AuditEvent(
            tenant_id=tenant_id,
            reimbursement_id=reimbursement_id,
            action=action,
            actor_id=actor_id,
            details=details or {},
        )

        self._events.append(
            event
        )

        return event

    def list_for_reimbursement(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
    ) -> list[AuditEvent]:

        return [
            event
            for event
            in self._events
            if (
                event.tenant_id
                == tenant_id
                and
                event.reimbursement_id
                == reimbursement_id
            )
        ]


class PostgresReimbursementAuditService:

    def record(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
        action: str,
        actor_id: str,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:

        event = AuditEvent(
            tenant_id=tenant_id,
            reimbursement_id=reimbursement_id,
            action=action,
            actor_id=actor_id,
            details=details or {},
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

        details_json = json.dumps(
            event.details,
            ensure_ascii=False,
            default=str,
        )

        with cursor_postgres(
            dict_cursor=False,
            commit_automatico=True,
        ) as cursor:

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

        return event

    def list_for_reimbursement(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
    ) -> list[AuditEvent]:

        sql = f"""
        SELECT
            event_id,
            tenant_id,
            reimbursement_id,
            action,
            actor_id,
            details,
            created_at

        FROM {REIMBURSEMENT_AUDIT_TABLE}

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

        events: list[
            AuditEvent
        ] = []

        for row in rows:

            item = dict(row)

            details = item.get(
                "details"
            )

            if isinstance(
                details,
                str,
            ):
                try:
                    details = json.loads(
                        details
                    )
                except json.JSONDecodeError:
                    details = {}

            if not isinstance(
                details,
                dict,
            ):
                details = {}

            events.append(
                AuditEvent(
                    event_id=str(
                        item["event_id"]
                    ),

                    tenant_id=str(
                        item["tenant_id"]
                    ),

                    reimbursement_id=str(
                        item[
                            "reimbursement_id"
                        ]
                    ),

                    action=str(
                        item["action"]
                    ),

                    actor_id=str(
                        item["actor_id"]
                    ),

                    details=details,

                    created_at=item[
                        "created_at"
                    ],
                )
            )

        return events