from __future__ import annotations

import json

from dataclasses import (
    dataclass,
    field,
)

from datetime import (
    datetime,
    timezone,
)

from uuid import uuid4

from src.database.connection import (
    cursor_postgres,
)

from .db_schema import (
    ORGANIZATION_AUDIT_TABLE,
)


def _utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


@dataclass(frozen=True)
class CorporateAuditEvent:
    organization_id: str
    action: str
    actor_user_id: str

    target_user_id: str | None = None

    details: dict = field(
        default_factory=dict
    )

    event_id: str = field(
        default_factory=lambda:
            str(uuid4())
    )

    created_at: datetime = field(
        default_factory=_utc_now
    )


class CorporateAuditService:

    def record(
        self,
        *,
        organization_id: str,
        action: str,
        actor_user_id: str,
        target_user_id: str | None = None,
        details: dict | None = None,
    ) -> CorporateAuditEvent:

        raise NotImplementedError

    def list_events(
        self,
        *,
        organization_id: str,
        limit: int = 100,
    ) -> list[CorporateAuditEvent]:

        raise NotImplementedError


class InMemoryCorporateAuditService(
    CorporateAuditService
):

    def __init__(self) -> None:
        self.events: list[
            CorporateAuditEvent
        ] = []

    def record(
        self,
        *,
        organization_id: str,
        action: str,
        actor_user_id: str,
        target_user_id: str | None = None,
        details: dict | None = None,
    ) -> CorporateAuditEvent:

        event = CorporateAuditEvent(
            organization_id=
                organization_id,

            action=
                action,

            actor_user_id=
                actor_user_id,

            target_user_id=
                target_user_id,

            details=
                details or {},
        )

        self.events.append(
            event
        )

        return event

    def list_events(
        self,
        *,
        organization_id: str,
        limit: int = 100,
    ) -> list[CorporateAuditEvent]:

        items = [
            event
            for event
            in self.events
            if (
                event.organization_id
                ==
                organization_id
            )
        ]

        items.sort(
            key=lambda event:
                event.created_at,
            reverse=True,
        )

        return items[
            :max(
                1,
                min(
                    int(limit),
                    500,
                ),
            )
        ]


class PostgresCorporateAuditService(
    CorporateAuditService
):

    def record(
        self,
        *,
        organization_id: str,
        action: str,
        actor_user_id: str,
        target_user_id: str | None = None,
        details: dict | None = None,
    ) -> CorporateAuditEvent:

        event = CorporateAuditEvent(
            organization_id=
                organization_id,

            action=
                action,

            actor_user_id=
                actor_user_id,

            target_user_id=
                target_user_id,

            details=
                details or {},
        )

        sql = f"""
        INSERT INTO {ORGANIZATION_AUDIT_TABLE} (
            event_id,
            organization_id,
            action,
            actor_user_id,
            target_user_id,
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

        with cursor_postgres(
            dict_cursor=False,
            commit_automatico=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    event.event_id,
                    event.organization_id,
                    event.action,
                    event.actor_user_id,
                    event.target_user_id,

                    json.dumps(
                        event.details,
                        ensure_ascii=False,
                        default=str,
                    ),

                    event.created_at,
                ),
            )

        return event

    def list_events(
        self,
        *,
        organization_id: str,
        limit: int = 100,
    ) -> list[CorporateAuditEvent]:

        safe_limit = max(
            1,
            min(
                int(limit),
                500,
            ),
        )

        sql = f"""
        SELECT
            event_id,
            organization_id,
            action,
            actor_user_id,
            target_user_id,
            details,
            created_at

        FROM {ORGANIZATION_AUDIT_TABLE}

        WHERE
            organization_id = %s

        ORDER BY
            created_at DESC

        LIMIT %s
        """

        with cursor_postgres(
            dict_cursor=True,
        ) as cursor:

            cursor.execute(
                sql,
                (
                    organization_id,
                    safe_limit,
                ),
            )

            rows = cursor.fetchall()

        events: list[
            CorporateAuditEvent
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
                    details = (
                        json.loads(
                            details
                        )
                    )

                except json.JSONDecodeError:
                    details = {}

            if not isinstance(
                details,
                dict,
            ):
                details = {}

            events.append(
                CorporateAuditEvent(
                    event_id=str(
                        item["event_id"]
                    ),

                    organization_id=str(
                        item[
                            "organization_id"
                        ]
                    ),

                    action=str(
                        item["action"]
                    ),

                    actor_user_id=str(
                        item[
                            "actor_user_id"
                        ]
                    ),

                    target_user_id=(
                        str(
                            item[
                                "target_user_id"
                            ]
                        )
                        if
                        item.get(
                            "target_user_id"
                        )
                        is not None
                        else None
                    ),

                    details=
                        details,

                    created_at=
                        item[
                            "created_at"
                        ],
                )
            )

        return events