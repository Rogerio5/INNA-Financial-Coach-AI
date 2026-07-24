from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from src.database.connection import (
    conexao_postgres,
    testar_conexao_postgres,
)


MIGRATION_PATH = Path(
    "scripts/sql/create_human_reviews.sql"
)

MIGRATION_NAME = (
    "inna:human_reviews:migration:v1"
)

EXPECTED_COLUMNS = {
    "id",
    "review_id",
    "thread_id",
    "status",
    "requested_by",
    "reason",
    "trigger",
    "risk_level",
    "payload",
    "allowed_actions",
    "decision_action",
    "reviewer_id",
    "reviewer_comment",
    "rejection_reason",
    "corrections",
    "resume_route",
    "processing_request_id",
    "processing_started_at",
    "failure_reason",
    "created_at",
    "updated_at",
    "resolved_at",
}

EXPECTED_INDEXES = {
    "uq_human_reviews_review_id",
    "idx_human_reviews_status_created_at",
    "idx_human_reviews_thread_id",
    "idx_human_reviews_reviewer_id",
    "idx_human_reviews_processing",
}


def _read_migration() -> str:
    if not MIGRATION_PATH.is_file():
        raise RuntimeError(
            "Arquivo da migration não encontrado: "
            f"{MIGRATION_PATH}"
        )

    sql = MIGRATION_PATH.read_text(
        encoding="utf-8-sig"
    ).strip()

    required = [
        (
            "CREATE TABLE IF NOT EXISTS "
            "public.human_reviews"
        ),
        "UNIQUE (review_id)",
        "payload JSONB",
        "corrections JSONB",
        "processing_request_id",
        "resume_failed",
    ]

    missing = [
        item
        for item in required
        if item not in sql
    ]

    if missing:
        raise RuntimeError(
            "Migration incompleta. Elementos "
            f"ausentes: {missing}"
        )

    return sql


def _controlled_sql(
    migration_sql: str,
) -> str:
    """
    Remove BEGIN e COMMIT do arquivo para que o
    runner controle integralmente a transação.
    """
    lines = migration_sql.splitlines()

    normalized = [
        line
        for line in lines
        if line.strip().upper()
        not in {
            "BEGIN;",
            "COMMIT;",
        }
    ]

    sql = "\n".join(
        normalized
    ).strip()

    if not sql:
        raise RuntimeError(
            "A migration ficou vazia após a "
            "normalização."
        )

    return sql


def _checksum(
    content: str,
) -> str:
    return hashlib.sha256(
        content.encode(
            "utf-8"
        )
    ).hexdigest()


def _table_exists(
    cursor: Any,
) -> bool:
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = 'human_reviews'
        );
        """
    )

    row = cursor.fetchone()

    return bool(
        row[0]
        if row
        else False
    )


def _columns(
    cursor: Any,
) -> set[str]:
    cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'human_reviews'
        ORDER BY ordinal_position;
        """
    )

    return {
        str(row[0])
        for row in cursor.fetchall()
    }


def _indexes(
    cursor: Any,
) -> set[str]:
    cursor.execute(
        """
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
          AND tablename = 'human_reviews';
        """
    )

    return {
        str(row[0])
        for row in cursor.fetchall()
    }


def _print_database_preflight() -> None:
    result = testar_conexao_postgres()

    if not result.get(
        "ok"
    ):
        raise RuntimeError(
            "A conexão PostgreSQL não foi "
            "validada."
        )

    print(
        "DATABASE_CONNECTION_OK"
    )

    print(
        "DATABASE:",
        result.get(
            "database"
        ),
    )

    print(
        "USER:",
        result.get(
            "user"
        ),
    )

    print(
        "SERVER_TIME:",
        result.get(
            "server_time"
        ),
    )


def check() -> None:
    migration_sql = _read_migration()

    print(
        "MIGRATION_PATH:",
        MIGRATION_PATH,
    )

    print(
        "MIGRATION_SHA256:",
        _checksum(
            migration_sql
        ),
    )

    _print_database_preflight()

    with conexao_postgres(
        commit_automatico=False,
    ) as connection:
        with connection.cursor() as cursor:
            exists = _table_exists(
                cursor
            )

            print(
                "TABLE_EXISTS:",
                exists,
            )

            if not exists:
                print(
                    "MIGRATION_REQUIRED: True"
                )

                print(
                    "HUMAN_REVIEW_MIGRATION_PREFLIGHT_OK"
                )

                return

            columns = _columns(
                cursor
            )

            indexes = _indexes(
                cursor
            )

            missing_columns = sorted(
                EXPECTED_COLUMNS
                - columns
            )

            missing_indexes = sorted(
                EXPECTED_INDEXES
                - indexes
            )

            print(
                "COLUMN_COUNT:",
                len(columns),
            )

            print(
                "INDEX_COUNT:",
                len(indexes),
            )

            print(
                "MISSING_COLUMNS:",
                missing_columns,
            )

            print(
                "MISSING_INDEXES:",
                missing_indexes,
            )

            migration_required = bool(
                missing_columns
                or missing_indexes
            )

            print(
                "MIGRATION_REQUIRED:",
                migration_required,
            )

            print(
                "HUMAN_REVIEW_MIGRATION_PREFLIGHT_OK"
            )


def apply() -> None:
    migration_sql = _read_migration()

    executable_sql = _controlled_sql(
        migration_sql
    )

    _print_database_preflight()

    with conexao_postgres(
        commit_automatico=False,
    ) as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT pg_advisory_xact_lock(
                        hashtext(%s)
                    );
                    """,
                    (
                        MIGRATION_NAME,
                    ),
                )

                cursor.execute(
                    "SET LOCAL lock_timeout "
                    "= '5000ms';"
                )

                cursor.execute(
                    "SET LOCAL statement_timeout "
                    "= '30000ms';"
                )

                cursor.execute(
                    executable_sql
                )

                if not _table_exists(
                    cursor
                ):
                    raise RuntimeError(
                        "A tabela human_reviews "
                        "não foi criada."
                    )

                columns = _columns(
                    cursor
                )

                indexes = _indexes(
                    cursor
                )

                missing_columns = (
                    EXPECTED_COLUMNS
                    - columns
                )

                missing_indexes = (
                    EXPECTED_INDEXES
                    - indexes
                )

                if missing_columns:
                    raise RuntimeError(
                        "Colunas ausentes após a "
                        "migration: "
                        f"{sorted(missing_columns)}"
                    )

                if missing_indexes:
                    raise RuntimeError(
                        "Índices ausentes após a "
                        "migration: "
                        f"{sorted(missing_indexes)}"
                    )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    print(
        "MIGRATION_SHA256:",
        _checksum(
            migration_sql
        ),
    )

    print(
        "HUMAN_REVIEW_MIGRATION_APPLIED"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Valida ou aplica a migration das "
            "revisões humanas da INNA."
        )
    )

    parser.add_argument(
        "action",
        choices=[
            "check",
            "apply",
        ],
    )

    args = parser.parse_args()

    try:
        if args.action == "check":
            check()
        else:
            apply()

    except Exception as exc:
        print(
            "MIGRATION_ERROR:",
            type(exc).__name__,
            str(exc),
            file=sys.stderr,
        )

        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
