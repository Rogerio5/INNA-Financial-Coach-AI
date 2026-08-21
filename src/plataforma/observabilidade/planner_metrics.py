"""
Métricas operacionais privacy-safe do Adaptive Planner.

O módulo persiste exclusivamente metadados técnicos
necessários para KPIs e SLOs do Planner.

Não armazena:
- pergunta;
- prompt;
- resposta;
- identidade do usuário;
- conteúdo financeiro.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from threading import RLock

from sqlalchemy import create_engine

PLANNER_METRICS_TABLE = (
    "planner_metric_events_inna"
)

_SUPPORTED_ROUTES = frozenset(
    {
        "deterministic",
        "gemini",
        "redis_hit",
        "fallback",
        "error",
    }
)

_SUPPORTED_SOURCES = frozenset(
    {
        "deterministic",
        "gemini",
        "cache",
        "none",
    }
)

_SUPPORTED_OUTCOMES = frozenset(
    {
        "success",
        "fallback",
        "error",
    }
)

_TABLE_LOCK = RLock()
_TABLE_READY = False


@dataclass(slots=True)
class PlannerMetricEvent:
    """
    Evento operacional sem conteúdo do usuário.
    """

    planner_mode: str
    query_complexity: str
    planner_route: str
    cache_hit: bool
    plan_source: str
    plan_valid: bool
    fallback_used: bool
    duration_ms: float
    planner_outcome: str = "success"

    def __post_init__(self) -> None:
        self.planner_mode = str(
            self.planner_mode
        ).strip()

        self.query_complexity = str(
            self.query_complexity
        ).strip()

        self.planner_route = str(
            self.planner_route
        ).strip()

        self.plan_source = str(
            self.plan_source
        ).strip()

        self.planner_outcome = str(
            self.planner_outcome
        ).strip()

        self.cache_hit = bool(
            self.cache_hit
        )

        self.plan_valid = bool(
            self.plan_valid
        )

        self.fallback_used = bool(
            self.fallback_used
        )

        try:
            duration = float(
                self.duration_ms
            )
        except (TypeError, ValueError):
            duration = 0.0

        self.duration_ms = max(
            duration,
            0.0,
        )

        if (
            self.planner_route
            not in _SUPPORTED_ROUTES
        ):
            raise ValueError(
                "unsupported_planner_route:"
                + self.planner_route
            )

        if (
            self.plan_source
            not in _SUPPORTED_SOURCES
        ):
            raise ValueError(
                "unsupported_plan_source:"
                + self.plan_source
            )

        if (
            self.planner_outcome
            not in _SUPPORTED_OUTCOMES
        ):
            raise ValueError(
                "unsupported_planner_outcome:"
                + self.planner_outcome
            )

        if self.planner_route == "error":
            if self.plan_source != "none":
                raise ValueError(
                    "invalid_error_plan_source:"
                    + self.plan_source
                )

            if self.planner_outcome != "error":
                raise ValueError(
                    "invalid_error_outcome:"
                    + self.planner_outcome
                )

            if self.plan_valid:
                raise ValueError(
                    "invalid_error_plan_valid"
                )

            if self.cache_hit:
                raise ValueError(
                    "invalid_error_cache_hit"
                )

            if self.fallback_used:
                raise ValueError(
                    "invalid_error_fallback_used"
                )


def _build_create_table_sql() -> str:
    """
    Retorna o DDL privacy-safe do repository.
    """

    return f"""
        CREATE TABLE IF NOT EXISTS {PLANNER_METRICS_TABLE} (
            id BIGSERIAL PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            planner_mode TEXT NOT NULL,
            query_complexity TEXT NOT NULL,
            planner_route TEXT NOT NULL,
            cache_hit BOOLEAN NOT NULL,
            plan_source TEXT NOT NULL,
            plan_valid BOOLEAN NOT NULL,
            fallback_used BOOLEAN NOT NULL,
            planner_outcome TEXT NOT NULL,
            duration_ms DOUBLE PRECISION NOT NULL
                CHECK (duration_ms >= 0)
        );

        CREATE INDEX IF NOT EXISTS
            idx_planner_metrics_created_at
        ON {PLANNER_METRICS_TABLE} (
            created_at DESC
        );

        CREATE INDEX IF NOT EXISTS
            idx_planner_metrics_route_created_at
        ON {PLANNER_METRICS_TABLE} (
            planner_route,
            created_at DESC
        );

        CREATE INDEX IF NOT EXISTS
            idx_planner_metrics_complexity_created_at
        ON {PLANNER_METRICS_TABLE} (
            query_complexity,
            created_at DESC
        );
    """


def _event_to_insert_payload(
    event: PlannerMetricEvent,
) -> dict[str, object]:
    """
    Converte o evento somente para campos técnicos.
    """

    return {
        "planner_mode": event.planner_mode,
        "query_complexity": (
            event.query_complexity
        ),
        "planner_route": event.planner_route,
        "cache_hit": event.cache_hit,
        "plan_source": event.plan_source,
        "plan_valid": event.plan_valid,
        "fallback_used": event.fallback_used,
        "duration_ms": event.duration_ms,
        "planner_outcome": event.planner_outcome,
    }


def _load_database_url() -> str:
    """
    Obtém DATABASE_URL do ambiente ou do .env
    sem expor a credencial.
    """

    database_url = (
        os.getenv("DATABASE_URL", "")
        .strip()
    )

    if database_url:
        return database_url

    try:
        from dotenv import load_dotenv

        load_dotenv(
            dotenv_path=".env",
            override=False,
        )
    except Exception:
        pass

    database_url = (
        os.getenv("DATABASE_URL", "")
        .strip()
    )

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL_not_configured"
        )

    return database_url


@lru_cache(maxsize=1)
def _database_engine():
    """
    Mantém um engine reutilizável por processo.
    """

    return create_engine(
        _load_database_url(),
        pool_pre_ping=True,
    )


def _connect_postgres():
    """
    Retorna uma conexão DBAPI PostgreSQL.
    """

    return (
        _database_engine()
        .raw_connection()
    )


def _ensure_table(
    connection,
) -> None:
    """
    Prepara a tabela somente uma vez por processo.

    Em caso de falha, o marcador não é ativado,
    permitindo nova tentativa futura.
    """

    global _TABLE_READY

    if _TABLE_READY:
        return

    with _TABLE_LOCK:
        if _TABLE_READY:
            return

        with connection.cursor() as cursor:
            cursor.execute(
                _build_create_table_sql()
            )

        _TABLE_READY = True


def _persist_event(
    event: PlannerMetricEvent,
) -> bool:
    """
    Persiste um evento operacional no PostgreSQL.

    Falhas são propagadas internamente para que
    record_planner_metric_event possa aplicar o
    contrato fail-open.
    """

    connection = _connect_postgres()

    try:
        _ensure_table(
            connection
        )

        payload = (
            _event_to_insert_payload(
                event
            )
        )

        statement = f"""
            INSERT INTO {PLANNER_METRICS_TABLE} (
                planner_mode,
                query_complexity,
                planner_route,
                cache_hit,
                plan_source,
                plan_valid,
                fallback_used,
                duration_ms,
                planner_outcome
            )
            VALUES (
                %(planner_mode)s,
                %(query_complexity)s,
                %(planner_route)s,
                %(cache_hit)s,
                %(plan_source)s,
                %(plan_valid)s,
                %(fallback_used)s,
                %(duration_ms)s,
                %(planner_outcome)s
            );
        """

        with connection.cursor() as cursor:
            cursor.execute(
                statement,
                payload,
            )

        connection.commit()

        return True

    except Exception:
        try:
            connection.rollback()
        except Exception:
            pass

        raise

    finally:
        try:
            connection.close()
        except Exception:
            pass


def _planner_metrics_enabled() -> bool:
    """
    Gate explícito da persistência operacional.

    Default seguro: desabilitado.
    """

    return (
        os.getenv(
            "INNA_PLANNER_METRICS_ENABLED",
            "false",
        )
        .strip()
        .lower()
        in {
            "1",
            "true",
            "yes",
            "on",
        }
    )


def record_planner_metric_event(
    event: PlannerMetricEvent,
) -> bool:
    """
    Fail-open: observabilidade nunca bloqueia
    a execução principal do Planner.
    """

    if not _planner_metrics_enabled():
        return False

    try:
        return bool(
            _persist_event(event)
        )
    except Exception:
        return False


__all__ = [
    "PLANNER_METRICS_TABLE",
    "PlannerMetricEvent",
    "record_planner_metric_event",
]
