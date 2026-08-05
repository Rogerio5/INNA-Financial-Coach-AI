from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.services.financial_history.repository import (
    FinancialHistoryQueryError,
    FinancialHistoryRepositoryError,
    SQL_CONSULTAR_HISTORICO_FINANCEIRO,
    consultar_historico_financeiro_usuario,
)


def _cursor_context(cursor):
    @contextmanager
    def manager():
        yield cursor

    return manager()


def test_executes_fixed_read_only_query():
    cursor = MagicMock()
    cursor.fetchall.return_value = []

    with patch(
        "src.services.financial_history.repository.cursor_postgres",
        return_value=_cursor_context(cursor),
    ) as mock_cursor_context:
        result = consultar_historico_financeiro_usuario(
            "  user-123  ",
            limite=3,
        )

    mock_cursor_context.assert_called_once_with(
        dict_cursor=True,
        commit_automatico=False,
    )

    assert cursor.execute.call_count == 3

    assert cursor.execute.call_args_list[0].args[0] == "SET TRANSACTION READ ONLY;"

    assert "statement_timeout" in cursor.execute.call_args_list[1].args[0]

    query_call = cursor.execute.call_args_list[2]

    assert query_call.args[0] == (SQL_CONSULTAR_HISTORICO_FINANCEIRO)

    assert query_call.args[1] == (
        "user-123",
        3,
    )

    normalized_sql = " ".join(SQL_CONSULTAR_HISTORICO_FINANCEIRO.upper().split())

    assert "SELECT *" not in normalized_sql

    assert "WHERE USUARIO_ID = %S" in normalized_sql

    assert "ORDER BY DATA_HORA DESC, ID DESC" in normalized_sql

    assert result == {
        "possui_historico": False,
        "total_retornado": 0,
        "diagnosticos": [],
    }


def test_rejects_missing_user_identity():
    with pytest.raises(FinancialHistoryQueryError):
        consultar_historico_financeiro_usuario("   ")


def test_rejects_oversized_user_identity():
    with pytest.raises(FinancialHistoryQueryError):
        consultar_historico_financeiro_usuario("x" * 161)


def test_rejects_boolean_limit():
    with pytest.raises(FinancialHistoryQueryError):
        consultar_historico_financeiro_usuario(
            "user-1",
            limite=True,
        )


def test_rejects_limit_below_range():
    with pytest.raises(FinancialHistoryQueryError):
        consultar_historico_financeiro_usuario(
            "user-1",
            limite=0,
        )


def test_rejects_limit_above_range():
    with pytest.raises(FinancialHistoryQueryError):
        consultar_historico_financeiro_usuario(
            "user-1",
            limite=21,
        )


def test_returns_only_allowlisted_fields():
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {
            "data_hora": datetime(
                2026,
                7,
                17,
                10,
                30,
            ),
            "saldo_estimado": Decimal("1200.50"),
            ("comprometimento_renda_percentual"): Decimal("70.25"),
            "meses_reserva_estimados": (Decimal("2.5")),
            "score_financeiro": 70,
            "nivel_risco": "Medio",
            "moeda": "BRL",
            "idioma": "pt",
            "nome": "Não deve sair",
            "objetivo": "Não deve sair",
            "diagnostico": "Não deve sair",
            "plano_30_dias": "Não deve sair",
            "usuario_id": "Não deve sair",
        }
    ]

    with patch(
        "src.services.financial_history.repository.cursor_postgres",
        return_value=_cursor_context(cursor),
    ):
        result = consultar_historico_financeiro_usuario("user-1")

    assert result["possui_historico"] is True

    assert result["total_retornado"] == 1

    item = result["diagnosticos"][0]

    assert item["data_hora"] == "2026-07-17T10:30:00"

    assert item["saldo_estimado"] == 1200.5

    assert item["score_financeiro"] == 70

    assert "nome" not in item
    assert "objetivo" not in item
    assert "diagnostico" not in item
    assert "plano_30_dias" not in item
    assert "usuario_id" not in item


def test_database_failure_becomes_safe_error():
    cursor = MagicMock()

    cursor.execute.side_effect = RuntimeError("postgresql://usuario:senha@servidor")

    with patch(
        "src.services.financial_history.repository.cursor_postgres",
        return_value=_cursor_context(cursor),
    ):
        with pytest.raises(FinancialHistoryRepositoryError) as exc_info:
            consultar_historico_financeiro_usuario("user-1")

    message = str(exc_info.value)

    assert message == ("Não foi possível consultar o histórico financeiro.")

    assert "senha" not in message
    assert "postgresql://" not in message


def test_repository_has_no_dynamic_table_name():
    source = Path("src/services/financial_history/repository.py").read_text(
        encoding="utf-8",
    )

    assert "FROM public.diagnosticos_financeiros" in source

    assert 'f"""' not in (SQL_CONSULTAR_HISTORICO_FINANCEIRO)
