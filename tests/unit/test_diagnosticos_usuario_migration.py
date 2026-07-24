from pathlib import Path

from sqlalchemy import String

from src.models import (
    DiagnosticoFinanceiro,
)


UP_MIGRATION = Path(
    "migrations/"
    "20260717_001_add_usuario_id_"
    "diagnosticos_financeiros.sql"
)

DOWN_MIGRATION = Path(
    "migrations/"
    "20260717_001_add_usuario_id_"
    "diagnosticos_financeiros.down.sql"
)


def _normalized_sql(
    path: Path,
) -> str:
    return " ".join(
        path.read_text(
            encoding="utf-8",
        ).upper().split()
    )


def test_model_has_nullable_user_identity():
    column = (
        DiagnosticoFinanceiro
        .__table__
        .columns["usuario_id"]
    )

    assert column.nullable is True
    assert isinstance(
        column.type,
        String,
    )
    assert column.type.length == 160


def test_legacy_model_mirrors_user_identity():
    source = Path(
        "src/models/legacy.py"
    ).read_text(
        encoding="utf-8",
    )

    assert (
        "usuario_id = Column("
        "String(160), nullable=True)"
        in source
    )


def test_up_migration_is_safe_and_idempotent():
    sql = _normalized_sql(
        UP_MIGRATION
    )

    assert (
        "ADD COLUMN IF NOT EXISTS "
        "USUARIO_ID VARCHAR(160)"
        in sql
    )

    assert (
        "CREATE INDEX IF NOT EXISTS "
        "IX_DIAGNOSTICOS_USUARIO_DATA"
        in sql
    )

    assert (
        "WHERE USUARIO_ID IS NOT NULL"
        in sql
    )

    assert (
        "CK_DIAGNOSTICOS_USUARIO_ID_FORMATO"
        in sql
    )

    # Registros antigos não podem ser ligados
    # automaticamente pelo campo nome.
    assert (
        "UPDATE PUBLIC."
        "DIAGNOSTICOS_FINANCEIROS"
        not in sql
    )

    assert "SET NOT NULL" not in sql


def test_down_migration_reverses_schema_objects():
    sql = _normalized_sql(
        DOWN_MIGRATION
    )

    assert (
        "DROP INDEX IF EXISTS PUBLIC."
        "IX_DIAGNOSTICOS_USUARIO_DATA"
        in sql
    )

    assert (
        "DROP CONSTRAINT IF EXISTS "
        "CK_DIAGNOSTICOS_USUARIO_ID_FORMATO"
        in sql
    )

    assert (
        "DROP COLUMN IF EXISTS USUARIO_ID"
        in sql
    )
