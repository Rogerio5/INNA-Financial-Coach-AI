"""Ledger PostgreSQL de confiabilidade de produção da INNA."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Final

from src.database.connection import (
    cursor_postgres,
)
from src.compartilhado.resilience import (
    ResilienceEvent,
    ResilienceEventType,
)

from .production_tracker import (
    PRODUCTION_RELIABILITY_POLICIES,
)

TABLE_NAME: Final = (
    "public.inna_production_reliability_events"
)

MAX_WINDOW_SECONDS: Final = (
    31 * 24 * 60 * 60
)


SQL_CREATE_TABLE: Final = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    event_id VARCHAR(128) PRIMARY KEY,

    operation VARCHAR(128) NOT NULL,

    outcome VARCHAR(16) NOT NULL
        CHECK (
            outcome IN (
                'succeeded',
                'failed'
            )
        ),

    circuit_rejected BOOLEAN NOT NULL
        DEFAULT FALSE,

    occurred_at TIMESTAMPTZ NOT NULL,

    recorded_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    CONSTRAINT
        chk_inna_reliability_operation
        CHECK (
            operation IN (
                'gemini.embedding',
                'gemini.generate.supervisor',
                'gemini.generate.text_service',
                'rag.agentic.planner'
            )
        ),

    CONSTRAINT
        chk_inna_reliability_event_id
        CHECK (
            char_length(event_id)
            BETWEEN 1 AND 128
        ),

    CONSTRAINT
        chk_inna_reliability_circuit_outcome
        CHECK (
            NOT circuit_rejected
            OR outcome = 'failed'
        )
);
"""


SQL_CREATE_OPERATION_TIME_INDEX: Final = f"""
CREATE INDEX IF NOT EXISTS
    idx_inna_reliability_operation_occurred_at
ON {TABLE_NAME} (
    operation,
    occurred_at DESC
);
"""


SQL_CREATE_FAILURE_TIME_INDEX: Final = f"""
CREATE INDEX IF NOT EXISTS
    idx_inna_reliability_failure_occurred_at
ON {TABLE_NAME} (
    operation,
    occurred_at DESC
)
WHERE outcome = 'failed';
"""


SQL_INSERT_EVENT: Final = f"""
INSERT INTO {TABLE_NAME} (
    event_id,
    operation,
    outcome,
    circuit_rejected,
    occurred_at
)
VALUES (
    %(event_id)s,
    %(operation)s,
    %(outcome)s,
    %(circuit_rejected)s,
    %(occurred_at)s
)
ON CONFLICT (event_id)
DO NOTHING
RETURNING
    event_id,
    recorded_at;
"""


SQL_WINDOW_AGGREGATE: Final = f"""
SELECT
    COUNT(*)::BIGINT
        AS total_operations,

    COUNT(*) FILTER (
        WHERE outcome = 'succeeded'
    )::BIGINT
        AS successful_operations,

    COUNT(*) FILTER (
        WHERE outcome = 'failed'
    )::BIGINT
        AS failed_operations,

    COUNT(*) FILTER (
        WHERE circuit_rejected
    )::BIGINT
        AS circuit_rejections,

    MIN(occurred_at)
        AS first_occurred_at,

    MAX(occurred_at)
        AS last_occurred_at

FROM {TABLE_NAME}

WHERE operation = %(operation)s

  AND occurred_at >= (
        NOW()
        - (
            %(window_seconds)s
            * INTERVAL '1 second'
        )
  )

  AND occurred_at <= NOW();
"""


class ProductionReliabilityRepositoryError(
    RuntimeError
):
    """
    Falha sanitizada do ledger.

    A mensagem pública nunca inclui SQL,
    DATABASE_URL ou mensagem bruta do driver.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class ProductionReliabilityLedgerWrite:
    event_id: str
    inserted: bool
    recorded_at: datetime | None


@dataclass(
    frozen=True,
    slots=True,
)
class ProductionReliabilityWindow:
    operation: str
    window_seconds: float

    total_operations: int
    successful_operations: int
    failed_operations: int
    circuit_rejections: int

    first_occurred_at: datetime | None
    last_occurred_at: datetime | None

    @property
    def observed_failure_ratio(
        self,
    ) -> float | None:
        if self.total_operations <= 0:
            return None

        return (
            self.failed_operations
            / self.total_operations
        )


def _validate_operation(
    operation: str,
) -> str:
    normalized = str(
        operation
    ).strip()

    if (
        normalized
        not in PRODUCTION_RELIABILITY_POLICIES
    ):
        raise ValueError(
            "Operation is not a tracked "
            "production reliability boundary."
        )

    return normalized


def _validate_window_seconds(
    window_seconds: float,
) -> float:
    parsed = float(
        window_seconds
    )

    if (
        not math.isfinite(parsed)
        or parsed <= 0
        or parsed > MAX_WINDOW_SECONDS
    ):
        raise ValueError(
            "window_seconds must be > 0 "
            "and <= 31 days."
        )

    return parsed


def _event_outcome(
    event: ResilienceEvent,
) -> tuple[str, bool]:
    if (
        event.event_type
        is ResilienceEventType
        .OPERATION_SUCCEEDED
    ):
        return (
            "succeeded",
            False,
        )

    if (
        event.event_type
        is ResilienceEventType
        .OPERATION_FAILED
    ):
        return (
            "failed",
            False,
        )

    if (
        event.event_type
        is ResilienceEventType
        .CIRCUIT_REJECTED
    ):
        return (
            "failed",
            True,
        )

    raise ValueError(
        "Only terminal resilience events "
        "can be persisted."
    )


def initialize_production_reliability_schema(
) -> None:
    """
    Cria tabela e índices idempotentemente.

    Não executa quando o módulo é importado.
    """
    try:
        with cursor_postgres(
            commit_automatico=True,
        ) as cursor:
            cursor.execute(
                SQL_CREATE_TABLE
            )

            cursor.execute(
                SQL_CREATE_OPERATION_TIME_INDEX
            )

            cursor.execute(
                SQL_CREATE_FAILURE_TIME_INDEX
            )

    except Exception as exc:
        raise (
            ProductionReliabilityRepositoryError(
                "Failed to initialize production "
                "reliability ledger."
            )
        ) from exc


def persist_production_reliability_event(
    event: ResilienceEvent,
) -> ProductionReliabilityLedgerWrite:
    """
    Persiste exatamente um evento terminal.

    event_id é a chave de idempotência real.
    """
    operation = _validate_operation(
        event.operation
    )

    (
        outcome,
        circuit_rejected,
    ) = _event_outcome(
        event
    )

    parameters = {
        "event_id": event.event_id,
        "operation": operation,
        "outcome": outcome,
        "circuit_rejected": (
            circuit_rejected
        ),
        "occurred_at": event.occurred_at,
    }

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            cursor.execute(
                SQL_INSERT_EVENT,
                parameters,
            )

            row = cursor.fetchone()

    except Exception as exc:
        raise (
            ProductionReliabilityRepositoryError(
                "Failed to persist production "
                "reliability event."
            )
        ) from exc

    if row is None:
        return ProductionReliabilityLedgerWrite(
            event_id=event.event_id,
            inserted=False,
            recorded_at=None,
        )

    return ProductionReliabilityLedgerWrite(
        event_id=str(
            row["event_id"]
        ),
        inserted=True,
        recorded_at=row[
            "recorded_at"
        ],
    )


def load_production_reliability_window(
    *,
    operation: str,
    window_seconds: float = 900.0,
) -> ProductionReliabilityWindow:
    """
    Consulta a janela compartilhada no PostgreSQL.

    A janela é calculada pelo relógio do banco,
    não pelo relógio local de uma réplica.
    """
    operation = _validate_operation(
        operation
    )

    window_seconds = (
        _validate_window_seconds(
            window_seconds
        )
    )

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=False,
        ) as cursor:
            cursor.execute(
                SQL_WINDOW_AGGREGATE,
                {
                    "operation": operation,
                    "window_seconds": (
                        window_seconds
                    ),
                },
            )

            row = cursor.fetchone()

    except Exception as exc:
        raise (
            ProductionReliabilityRepositoryError(
                "Failed to load production "
                "reliability window."
            )
        ) from exc

    row = row or {}

    total = int(
        row.get(
            "total_operations",
            0,
        )
        or 0
    )

    successful = int(
        row.get(
            "successful_operations",
            0,
        )
        or 0
    )

    failed = int(
        row.get(
            "failed_operations",
            0,
        )
        or 0
    )

    circuit = int(
        row.get(
            "circuit_rejections",
            0,
        )
        or 0
    )

    if (
        successful + failed
        != total
    ):
        raise (
            ProductionReliabilityRepositoryError(
                "Reliability ledger aggregate "
                "is inconsistent."
            )
        )

    if circuit > failed:
        raise (
            ProductionReliabilityRepositoryError(
                "Reliability circuit aggregate "
                "is inconsistent."
            )
        )

    return ProductionReliabilityWindow(
        operation=operation,
        window_seconds=window_seconds,
        total_operations=total,
        successful_operations=successful,
        failed_operations=failed,
        circuit_rejections=circuit,
        first_occurred_at=row.get(
            "first_occurred_at"
        ),
        last_occurred_at=row.get(
            "last_occurred_at"
        ),
    )


__all__ = [
    "MAX_WINDOW_SECONDS",
    "ProductionReliabilityLedgerWrite",
    "ProductionReliabilityRepositoryError",
    "ProductionReliabilityWindow",
    "SQL_CREATE_FAILURE_TIME_INDEX",
    "SQL_CREATE_OPERATION_TIME_INDEX",
    "SQL_CREATE_TABLE",
    "SQL_INSERT_EVENT",
    "SQL_WINDOW_AGGREGATE",
    "TABLE_NAME",
    "initialize_production_reliability_schema",
    "load_production_reliability_window",
    "persist_production_reliability_event",
]
