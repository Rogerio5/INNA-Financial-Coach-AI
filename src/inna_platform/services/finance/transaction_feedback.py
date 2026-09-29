from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4


FEEDBACK_TABLE = (
    "inna_transaction_classification_feedback"
)

IDENTITY_SCOPE = "anonymous_global"

VALID_SOURCES = {
    "financeiro_ui",
    "tc3_validation",
}


def _database():
    try:
        from src.database.connection import (
            cursor_postgres,
            obter_database_url,
        )
    except ImportError:
        from database.connection import (
            cursor_postgres,
            obter_database_url,
        )

    return (
        cursor_postgres,
        obter_database_url,
    )


def _official_categories() -> set[str]:

    from src.inna_platform.services.finance.transaction_semantic_classifier import (
        OFFICIAL_EXPENSE_CATEGORIES,
    )

    return set(
        OFFICIAL_EXPENSE_CATEGORIES
    )


def ensure_feedback_schema() -> None:

    cursor_postgres, _ = _database()

    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {FEEDBACK_TABLE} (
        event_id TEXT PRIMARY KEY,

        created_at TIMESTAMPTZ
            NOT NULL
            DEFAULT CURRENT_TIMESTAMP,

        classifier_version TEXT
            NOT NULL,

        identity_scope TEXT
            NOT NULL,

        feedback_type TEXT
            NOT NULL
            CHECK (
                feedback_type IN (
                    'accepted',
                    'corrected'
                )
            ),

        suggested_category TEXT
            NOT NULL,

        final_category TEXT
            NOT NULL,

        strategy TEXT
            NOT NULL,

        confidence DOUBLE PRECISION
            NOT NULL,

        semantic_similarity DOUBLE PRECISION
            NULL,

        semantic_margin DOUBLE PRECISION
            NULL,

        needs_confirmation BOOLEAN
            NOT NULL,

        transaction_type TEXT
            NOT NULL,

        source TEXT
            NOT NULL
    )
    """

    index_created = f"""
    CREATE INDEX IF NOT EXISTS
        idx_inna_transaction_feedback_created
    ON {FEEDBACK_TABLE} (
        created_at DESC
    )
    """

    index_category = f"""
    CREATE INDEX IF NOT EXISTS
        idx_inna_transaction_feedback_category
    ON {FEEDBACK_TABLE} (
        final_category
    )
    """

    index_type = f"""
    CREATE INDEX IF NOT EXISTS
        idx_inna_transaction_feedback_type
    ON {FEEDBACK_TABLE} (
        feedback_type
    )
    """

    with cursor_postgres() as cursor:

        cursor.execute(
            create_sql
        )

        cursor.execute(
            index_created
        )

        cursor.execute(
            index_category
        )

        cursor.execute(
            index_type
        )


def build_feedback_event(
    *,
    classification: Mapping[str, Any],
    final_category: str,
    transaction_type: str,
    source: str = "financeiro_ui",
) -> dict[str, Any]:

    final_category = str(
        final_category or ""
    ).strip()

    if (
        final_category
        not in _official_categories()
    ):
        raise ValueError(
            "Categoria final inválida."
        )

    source = str(
        source or ""
    ).strip()

    if source not in VALID_SOURCES:
        raise ValueError(
            "Origem de feedback inválida."
        )

    category = str(
        classification.get(
            "category",
            "",
        )
        or ""
    ).strip()

    semantic_suggestion = str(
        classification.get(
            "suggested_category",
            "",
        )
        or ""
    ).strip()

    suggested_category = (
        semantic_suggestion
        or category
    )

    if not suggested_category:
        raise ValueError(
            "Classificação sem categoria sugerida."
        )

    feedback_type = (
        "accepted"
        if final_category
        == suggested_category
        else "corrected"
    )

    confidence = float(
        classification.get(
            "confidence",
            0.0,
        )
        or 0.0
    )

    semantic_similarity = (
        classification.get(
            "semantic_similarity"
        )
    )

    if semantic_similarity is not None:
        semantic_similarity = float(
            semantic_similarity
        )

    semantic_margin = (
        classification.get(
            "semantic_margin"
        )
    )

    if semantic_margin is not None:
        semantic_margin = float(
            semantic_margin
        )

    strategy = str(
        classification.get(
            "strategy",
            "unknown",
        )
        or "unknown"
    )

    needs_confirmation = bool(
        classification.get(
            "needs_confirmation",
            True,
        )
    )

    return {
        "event_id": uuid4().hex,
        "created_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "classifier_version": "tc2",
        "identity_scope": (
            IDENTITY_SCOPE
        ),
        "feedback_type": (
            feedback_type
        ),
        "suggested_category": (
            suggested_category
        ),
        "final_category": (
            final_category
        ),
        "strategy": strategy,
        "confidence": confidence,
        "semantic_similarity": (
            semantic_similarity
        ),
        "semantic_margin": (
            semantic_margin
        ),
        "needs_confirmation": (
            needs_confirmation
        ),
        "transaction_type": str(
            transaction_type
            or "Despesa"
        ),
        "source": source,
    }


def persist_feedback_event(
    event: Mapping[str, Any],
) -> dict[str, Any]:

    ensure_feedback_schema()

    cursor_postgres, _ = _database()

    sql = f"""
    INSERT INTO {FEEDBACK_TABLE} (
        event_id,
        classifier_version,
        identity_scope,
        feedback_type,
        suggested_category,
        final_category,
        strategy,
        confidence,
        semantic_similarity,
        semantic_margin,
        needs_confirmation,
        transaction_type,
        source
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

    params = (
        event["event_id"],
        event["classifier_version"],
        event["identity_scope"],
        event["feedback_type"],
        event["suggested_category"],
        event["final_category"],
        event["strategy"],
        event["confidence"],
        event["semantic_similarity"],
        event["semantic_margin"],
        event["needs_confirmation"],
        event["transaction_type"],
        event["source"],
    )

    with cursor_postgres() as cursor:

        cursor.execute(
            sql,
            params,
        )

    return dict(
        event
    )


def record_classification_feedback(
    *,
    description: str,
    final_category: str,
    transaction_type: str = "Despesa",
    merchant: str = "",
    amount: float | None = None,
    source: str = "financeiro_ui",
) -> dict[str, Any]:

    from src.inna_platform.services.finance.transaction_semantic_classifier import (
        classify_transaction_intelligent,
    )

    classification = (
        classify_transaction_intelligent(
            description=description,
            transaction_type=(
                transaction_type
            ),
            merchant=merchant,
            amount=amount,
        )
    )

    event = build_feedback_event(
        classification=(
            classification.to_dict()
        ),
        final_category=(
            final_category
        ),
        transaction_type=(
            transaction_type
        ),
        source=source,
    )

    return persist_feedback_event(
        event
    )


def delete_feedback_event(
    event_id: str,
) -> None:

    cursor_postgres, _ = _database()

    sql = f"""
    DELETE FROM {FEEDBACK_TABLE}
    WHERE event_id = %s
    """

    with cursor_postgres() as cursor:

        cursor.execute(
            sql,
            (
                str(event_id),
            ),
        )


def feedback_capabilities() -> dict:

    database_configured = False

    try:

        _, obter_database_url = (
            _database()
        )

        database_configured = bool(
            obter_database_url(
                obrigatoria=False
            )
        )

    except Exception:
        database_configured = False

    return {
        "version": "tc3",
        "feedback_enabled": True,
        "persistence": "postgresql",
        "database_configured": (
            database_configured
        ),
        "identity_scope": (
            IDENTITY_SCOPE
        ),
        "user_identity_enabled": False,
        "personal_learning": False,
        "raw_description_stored": False,
        "merchant_stored": False,
        "amount_stored": False,
        "accepted_feedback": True,
        "corrected_feedback": True,
    }


__all__ = [
    "FEEDBACK_TABLE",
    "IDENTITY_SCOPE",
    "ensure_feedback_schema",
    "build_feedback_event",
    "persist_feedback_event",
    "record_classification_feedback",
    "delete_feedback_event",
    "feedback_capabilities",
]