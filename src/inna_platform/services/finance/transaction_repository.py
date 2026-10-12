from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any
from uuid import uuid4

from src.database.connection import (
    cursor_postgres,
    obter_database_url,
)

from src.inna_platform.services.finance.transaction_semantic_classifier import (
    OFFICIAL_EXPENSE_CATEGORIES,
)


TRANSACTION_TABLE = "inna_financial_transactions"

TRANSACTION_REPOSITORY_VERSION = "tc4-a2"

SUPPORTED_TRANSACTION_TYPES = {
    "Despesa",
}

VALID_SOURCES = {
    "financeiro_ui",
    "api",
    "import",
    "tc4_validation",
}


_RETURNING_COLUMNS = (
    "transaction_id",
    "owner_id",
    "transaction_date",
    "transaction_type",
    "amount",
    "currency",
    "description",
    "merchant",
    "category",
    "subcategory",
    "classification_strategy",
    "classification_confidence",
    "semantic_similarity",
    "semantic_margin",
    "classification_confirmed",
    "source",
    "created_at",
    "updated_at",
)


def _database_configured() -> bool:

    try:

        return bool(
            obter_database_url(
                obrigatoria=False
            )
        )

    except Exception:

        return False


def _normalize_text(
    value: Any,
) -> str:

    if value is None:
        return ""

    return str(
        value
    ).strip()


def _normalize_amount(
    value: Any,
) -> Decimal:

    try:

        amount = Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ) as exc:

        raise ValueError(
            "amount inválido"
        ) from exc

    if not amount.is_finite() or amount <= 0 or amount >= Decimal("1000000000000"):
        raise ValueError("Valor deve ser positivo e menor que 1 trilhão")
    amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if amount <= 0 or amount >= Decimal("1000000000000"):
        raise ValueError("Valor fora do intervalo permitido")

    return amount


def _normalize_currency(
    value: Any,
) -> str:

    currency = (
        _normalize_text(
            value
        )
        or "BRL"
    ).upper()

    if (
        len(currency) != 3
        or not currency.isalpha()
    ):

        raise ValueError(
            "currency deve possuir 3 letras"
        )

    return currency


def _normalize_transaction_date(
    value: Any,
) -> date:

    if value is None:

        return date.today()

    if isinstance(
        value,
        datetime,
    ):

        return value.date()

    if isinstance(
        value,
        date,
    ):

        return value

    text = _normalize_text(
        value
    )

    try:

        return date.fromisoformat(
            text
        )

    except ValueError as exc:

        raise ValueError(
            "transaction_date deve usar YYYY-MM-DD"
        ) from exc


def _normalize_optional_float(
    value: Any,
) -> float | None:

    if value is None:
        return None

    numeric = float(
        value
    )

    if not 0.0 <= numeric <= 1.0:

        raise ValueError(
            "métrica de classificação fora do intervalo 0..1"
        )

    return numeric


def _serialize_value(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Decimal,
    ):

        return float(
            value
        )

    if isinstance(
        value,
        (
            date,
            datetime,
        ),
    ):

        return value.isoformat()

    return value


def _row_to_dict(
    row: tuple[Any, ...] | None,
) -> dict[str, Any] | None:

    if row is None:
        return None

    return {
        key: _serialize_value(
            value
        )
        for key, value in zip(
            _RETURNING_COLUMNS,
            row,
        )
    }


def build_financial_transaction(
    *,
    owner_id: str,
    amount: Any,
    description: str,
    category: str,
    transaction_type: str = "Despesa",
    currency: str = "BRL",
    transaction_date: Any = None,
    merchant: str = "",
    subcategory: str = "",
    classification_strategy: str = "manual",
    classification_confidence: Any = None,
    semantic_similarity: Any = None,
    semantic_margin: Any = None,
    classification_confirmed: bool = True,
    source: str = "api",
    transaction_id: str | None = None,
) -> dict[str, Any]:

    normalized_owner_id = _normalize_text(
        owner_id
    )

    if not normalized_owner_id:

        raise ValueError(
            "owner_id é obrigatório"
        )

    normalized_type = _normalize_text(
        transaction_type
    )

    if (
        normalized_type
        not in SUPPORTED_TRANSACTION_TYPES
    ):

        raise ValueError(
            "transaction_type ainda não suportado"
        )

    normalized_description = _normalize_text(
        description
    )

    if not normalized_description:

        raise ValueError(
            "description é obrigatória"
        )

    normalized_category = _normalize_text(
        category
    )

    if (
        normalized_category
        not in OFFICIAL_EXPENSE_CATEGORIES
    ):

        raise ValueError(
            "categoria de despesa inválida"
        )

    normalized_source = _normalize_text(
        source
    )

    if (
        normalized_source
        not in VALID_SOURCES
    ):

        raise ValueError(
            "source inválido"
        )

    normalized_strategy = (
        _normalize_text(
            classification_strategy
        )
        or "manual"
    )

    return {
        "transaction_id": (
            _normalize_text(
                transaction_id
            )
            or uuid4().hex
        ),
        "owner_id": normalized_owner_id,
        "transaction_date": (
            _normalize_transaction_date(
                transaction_date
            )
        ),
        "transaction_type": normalized_type,
        "amount": _normalize_amount(
            amount
        ),
        "currency": _normalize_currency(
            currency
        ),
        "description": normalized_description,
        "merchant": (
            _normalize_text(
                merchant
            )
            or None
        ),
        "category": normalized_category,
        "subcategory": (
            _normalize_text(
                subcategory
            )
            or None
        ),
        "classification_strategy": (
            normalized_strategy
        ),
        "classification_confidence": (
            _normalize_optional_float(
                classification_confidence
            )
        ),
        "semantic_similarity": (
            _normalize_optional_float(
                semantic_similarity
            )
        ),
        "semantic_margin": (
            _normalize_optional_float(
                semantic_margin
            )
        ),
        "classification_confirmed": bool(
            classification_confirmed
        ),
        "source": normalized_source,
    }


def ensure_transaction_schema() -> None:

    sql = f"""
    CREATE TABLE IF NOT EXISTS {TRANSACTION_TABLE} (
        transaction_id TEXT PRIMARY KEY,

        owner_id TEXT NOT NULL,

        transaction_date DATE NOT NULL,

        transaction_type TEXT NOT NULL
            CHECK (
                transaction_type
                IN ('Despesa')
            ),

        amount NUMERIC(14, 2) NOT NULL
            CHECK (
                amount > 0
            ),

        currency VARCHAR(3) NOT NULL,

        description TEXT NOT NULL,

        merchant TEXT NULL,

        category TEXT NOT NULL,

        subcategory TEXT NULL,

        classification_strategy TEXT NOT NULL,

        classification_confidence DOUBLE PRECISION NULL
            CHECK (
                classification_confidence IS NULL
                OR (
                    classification_confidence >= 0
                    AND classification_confidence <= 1
                )
            ),

        semantic_similarity DOUBLE PRECISION NULL
            CHECK (
                semantic_similarity IS NULL
                OR (
                    semantic_similarity >= 0
                    AND semantic_similarity <= 1
                )
            ),

        semantic_margin DOUBLE PRECISION NULL
            CHECK (
                semantic_margin IS NULL
                OR (
                    semantic_margin >= 0
                    AND semantic_margin <= 1
                )
            ),

        classification_confirmed BOOLEAN NOT NULL
            DEFAULT FALSE,

        source TEXT NOT NULL,

        created_at TIMESTAMPTZ NOT NULL
            DEFAULT CURRENT_TIMESTAMP,

        updated_at TIMESTAMPTZ NOT NULL
            DEFAULT CURRENT_TIMESTAMP
    )
    """

    index_owner_date = f"""
    CREATE INDEX IF NOT EXISTS
        idx_inna_financial_transactions_owner_date
    ON {TRANSACTION_TABLE} (
        owner_id,
        transaction_date DESC
    )
    """

    index_owner_category = f"""
    CREATE INDEX IF NOT EXISTS
        idx_inna_financial_transactions_owner_category
    ON {TRANSACTION_TABLE} (
        owner_id,
        category
    )
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql
        )

        cursor.execute(
            index_owner_date
        )

        cursor.execute(
            index_owner_category
        )


def create_financial_transaction(
    **kwargs: Any,
) -> dict[str, Any]:

    record = build_financial_transaction(
        **kwargs
    )

    ensure_transaction_schema()

    sql = f"""
    INSERT INTO {TRANSACTION_TABLE} (
        transaction_id,
        owner_id,
        transaction_date,
        transaction_type,
        amount,
        currency,
        description,
        merchant,
        category,
        subcategory,
        classification_strategy,
        classification_confidence,
        semantic_similarity,
        semantic_margin,
        classification_confirmed,
        source
    )
    VALUES (
        %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s
    )
    RETURNING
        transaction_id,
        owner_id,
        transaction_date,
        transaction_type,
        amount,
        currency,
        description,
        merchant,
        category,
        subcategory,
        classification_strategy,
        classification_confidence,
        semantic_similarity,
        semantic_margin,
        classification_confirmed,
        source,
        created_at,
        updated_at
    """

    params = (
        record["transaction_id"],
        record["owner_id"],
        record["transaction_date"],
        record["transaction_type"],
        record["amount"],
        record["currency"],
        record["description"],
        record["merchant"],
        record["category"],
        record["subcategory"],
        record["classification_strategy"],
        record["classification_confidence"],
        record["semantic_similarity"],
        record["semantic_margin"],
        record["classification_confirmed"],
        record["source"],
    )

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            params,
        )

        row = cursor.fetchone()

    result = _row_to_dict(
        row
    )

    if result is None:

        raise RuntimeError(
            "transação não retornada pelo PostgreSQL"
        )

    return result


def get_financial_transaction(
    *,
    owner_id: str,
    transaction_id: str,
) -> dict[str, Any] | None:

    normalized_owner_id = _normalize_text(
        owner_id
    )

    normalized_transaction_id = _normalize_text(
        transaction_id
    )

    if not normalized_owner_id:

        raise ValueError(
            "owner_id é obrigatório"
        )

    if not normalized_transaction_id:

        raise ValueError(
            "transaction_id é obrigatório"
        )

    sql = f"""
    SELECT
        transaction_id,
        owner_id,
        transaction_date,
        transaction_type,
        amount,
        currency,
        description,
        merchant,
        category,
        subcategory,
        classification_strategy,
        classification_confidence,
        semantic_similarity,
        semantic_margin,
        classification_confirmed,
        source,
        created_at,
        updated_at
    FROM {TRANSACTION_TABLE}
    WHERE owner_id = %s
      AND transaction_id = %s
    LIMIT 1
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (
                normalized_owner_id,
                normalized_transaction_id,
            ),
        )

        row = cursor.fetchone()

    return _row_to_dict(
        row
    )


def list_financial_transactions(
    *,
    owner_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:

    normalized_owner_id = _normalize_text(
        owner_id
    )

    if not normalized_owner_id:

        raise ValueError(
            "owner_id é obrigatório"
        )

    normalized_limit = int(
        limit
    )

    if normalized_limit < 1:

        normalized_limit = 1

    if normalized_limit > 200:

        normalized_limit = 200

    sql = f"""
    SELECT
        transaction_id,
        owner_id,
        transaction_date,
        transaction_type,
        amount,
        currency,
        description,
        merchant,
        category,
        subcategory,
        classification_strategy,
        classification_confidence,
        semantic_similarity,
        semantic_margin,
        classification_confirmed,
        source,
        created_at,
        updated_at
    FROM {TRANSACTION_TABLE}
    WHERE owner_id = %s
    ORDER BY
        transaction_date DESC,
        created_at DESC
    LIMIT %s
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=False,
    ) as cursor:

        cursor.execute(
            sql,
            (
                normalized_owner_id,
                normalized_limit,
            ),
        )

        rows = cursor.fetchall()

    return [
        _row_to_dict(
            row
        )
        for row in rows
    ]


def delete_financial_transaction(
    *,
    owner_id: str,
    transaction_id: str,
) -> bool:

    normalized_owner_id = _normalize_text(
        owner_id
    )

    normalized_transaction_id = _normalize_text(
        transaction_id
    )

    if not normalized_owner_id:

        raise ValueError(
            "owner_id é obrigatório"
        )

    if not normalized_transaction_id:

        raise ValueError(
            "transaction_id é obrigatório"
        )

    sql = f"""
    DELETE FROM {TRANSACTION_TABLE}
    WHERE owner_id = %s
      AND transaction_id = %s
    """

    with cursor_postgres(
        dict_cursor=False,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            (
                normalized_owner_id,
                normalized_transaction_id,
            ),
        )

        deleted = (
            cursor.rowcount
            > 0
        )

    return deleted


def transaction_repository_capabilities() -> dict[str, Any]:

    return {
        "version": TRANSACTION_REPOSITORY_VERSION,
        "table": TRANSACTION_TABLE,
        "persistence": "postgresql",
        "database_configured": _database_configured(),
        "single_source_ready": True,
        "expense_transactions": True,
        "income_transactions": False,
        "owner_id_required": True,
        "owner_identity_verified_here": False,
        "trusted_server_identity_required": True,
        "public_write_endpoint": False,
        "browser_user_id_allowed": False,
        "raw_description_stored": True,
        "merchant_stored": True,
        "classification_metadata_stored": True,
        "personal_learning": False,
    }
# SABINO_MONTHLY_EXPENSE_SUMMARY_V1

def summarize_financial_expenses_by_month(
    *,
    owner_id: str,
    reference_month: str,
) -> dict:
    import re

    owner_id = str(owner_id).strip()
    reference_month = str(reference_month).strip()

    if not owner_id:
        raise ValueError("owner_id é obrigatório")

    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", reference_month):
        raise ValueError("reference_month inválido")

    sql = f"""
    SELECT
        COALESCE(SUM(amount), 0) AS total_spent,
        COUNT(*) AS transaction_count
    FROM {TRANSACTION_TABLE}
    WHERE owner_id = %s
      AND transaction_type = 'Despesa'
      AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
    """

    sql_categories = f"""
    SELECT
        category,
        COALESCE(SUM(amount), 0) AS total_spent,
        COUNT(*) AS transaction_count
    FROM {TRANSACTION_TABLE}
    WHERE owner_id = %s
      AND transaction_type = 'Despesa'
      AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
    GROUP BY category
    ORDER BY category
    """

    with cursor_postgres(dict_cursor=True) as cursor:
        cursor.execute(sql, (owner_id, reference_month))
        summary = dict(cursor.fetchone())

        cursor.execute(
            sql_categories,
            (owner_id, reference_month),
        )

        categories = [
            dict(row)
            for row in cursor.fetchall()
        ]

    return {
        "reference_month": reference_month,
        "total_spent": summary["total_spent"],
        "transaction_count": summary["transaction_count"],
        "categories": categories,
    }
# SABINO_MONTHLY_EXPENSE_LIST_V1

def list_financial_expenses_by_month(
    *,
    owner_id: str,
    reference_month: str,
) -> list[dict]:
    import re
    from datetime import date

    owner_id = str(owner_id).strip()
    reference_month = str(reference_month).strip()

    if not owner_id:
        raise ValueError("owner_id é obrigatório")

    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", reference_month):
        raise ValueError("reference_month inválido")

    year, month = map(int, reference_month.split("-"))
    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    sql = f"""
    SELECT
        transaction_id,
        transaction_date,
        transaction_type,
        amount,
        currency,
        description,
        merchant,
        category,
        subcategory
    FROM {TRANSACTION_TABLE}
    WHERE owner_id = %s
      AND transaction_type = 'Despesa'
      AND transaction_date >= %s
      AND transaction_date < %s
    ORDER BY transaction_date DESC, transaction_id DESC
    """

    with cursor_postgres(dict_cursor=True) as cursor:
        cursor.execute(
            sql,
            (
                owner_id,
                start_date,
                end_date,
            ),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]
# SABINO_IDEMPOTENT_TRANSACTION_V1

def create_financial_transaction_idempotent(
    **kwargs: Any,
) -> dict[str, Any]:

    transaction_id = str(
        kwargs.get("transaction_id") or ""
    ).strip()

    if not transaction_id:
        raise ValueError(
            "transaction_id é obrigatório para operação idempotente"
        )

    record = build_financial_transaction(
        **kwargs
    )

    ensure_transaction_schema()

    sql = f"""
    INSERT INTO {TRANSACTION_TABLE} (
        transaction_id,
        owner_id,
        transaction_date,
        transaction_type,
        amount,
        currency,
        description,
        merchant,
        category,
        subcategory,
        classification_strategy,
        classification_confidence,
        semantic_similarity,
        semantic_margin,
        classification_confirmed,
        source
    )
    VALUES (
        %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s
    )

    ON CONFLICT (transaction_id)
    DO NOTHING

    RETURNING
        transaction_id,
        owner_id,
        transaction_date,
        transaction_type,
        amount,
        currency,
        description,
        merchant,
        category,
        subcategory,
        classification_strategy,
        classification_confidence,
        semantic_similarity,
        semantic_margin,
        classification_confirmed,
        source,
        created_at,
        updated_at
    """

    params = (
        record["transaction_id"],
        record["owner_id"],
        record["transaction_date"],
        record["transaction_type"],
        record["amount"],
        record["currency"],
        record["description"],
        record["merchant"],
        record["category"],
        record["subcategory"],
        record["classification_strategy"],
        record["classification_confidence"],
        record["semantic_similarity"],
        record["semantic_margin"],
        record["classification_confirmed"],
        record["source"],
    )

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:

        cursor.execute(
            sql,
            params,
        )

        row = cursor.fetchone()

        if row:
            result = dict(row)
            result["already_existed"] = False
            return result

        cursor.execute(
            f"""
            SELECT
                transaction_id,
                owner_id,
                transaction_date,
                transaction_type,
                amount,
                currency,
                description,
                merchant,
                category,
                subcategory,
                classification_strategy,
                classification_confidence,
                semantic_similarity,
                semantic_margin,
                classification_confirmed,
                source,
                created_at,
                updated_at
            FROM {TRANSACTION_TABLE}
            WHERE transaction_id = %s
              AND owner_id = %s
            LIMIT 1
            """,
            (
                transaction_id,
                record["owner_id"],
            ),
        )

        existing = cursor.fetchone()

        if not existing:
            raise RuntimeError(
                "Falha ao recuperar transação idempotente"
            )

        result = dict(existing)
        result["already_existed"] = True

        return result


def update_financial_transaction(*, owner_id, transaction_id, amount, description, category, transaction_date):
    """Edit a BRL expense using server-resolved ownership in the same statement."""
    if not str(transaction_id).strip():
        raise ValueError("transaction_id é obrigatório")
    data = build_financial_transaction(
        owner_id=owner_id, amount=amount, description=description,
        category=category, transaction_date=transaction_date,
    )
    sql = f"""
        UPDATE {TRANSACTION_TABLE}
        SET amount = %s, description = %s, category = %s, transaction_date = %s,
            classification_strategy = 'manual', classification_confirmed = TRUE,
            classification_confidence = NULL, semantic_similarity = NULL,
            semantic_margin = NULL, subcategory = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE owner_id = %s AND transaction_id = %s
          AND transaction_type = 'Despesa' AND currency = 'BRL'
        RETURNING {', '.join(_RETURNING_COLUMNS)}
    """
    with cursor_postgres(dict_cursor=False, commit_automatico=True) as cursor:
        cursor.execute(sql, (data['amount'], data['description'], data['category'],
                            data['transaction_date'], data['owner_id'], str(transaction_id).strip()))
        return _row_to_dict(cursor.fetchone())
