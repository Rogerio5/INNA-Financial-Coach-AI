"""
Repositório PostgreSQL read-only do histórico financeiro.

Regras:
- identidade obrigatória;
- nenhuma pesquisa por nome;
- SQL fixo e parametrizado;
- transação explicitamente somente leitura;
- limite máximo de registros;
- retorno mínimo, sem textos extensos ou PII.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from math import isfinite
from typing import Any

from src.database.connection import (
    cursor_postgres,
)


DEFAULT_HISTORY_LIMIT = 5
MAX_HISTORY_LIMIT = 20
MAX_USER_ID_LENGTH = 160

SQL_CONSULTAR_HISTORICO_FINANCEIRO = """
SELECT
    data_hora,
    saldo_estimado,
    comprometimento_renda_percentual,
    meses_reserva_estimados,
    score_financeiro,
    nivel_risco,
    moeda,
    idioma
FROM public.diagnosticos_financeiros
WHERE usuario_id = %s
ORDER BY
    data_hora DESC,
    id DESC
LIMIT %s;
"""


class FinancialHistoryQueryError(ValueError):
    """Consulta de histórico inválida."""


class FinancialHistoryRepositoryError(RuntimeError):
    """Falha segura de acesso ao histórico."""


def _normalizar_usuario_id(
    usuario_id: Any,
) -> str:
    value = str(usuario_id or "").strip()

    if not value:
        raise FinancialHistoryQueryError("A identidade do usuário é obrigatória.")

    if len(value) > MAX_USER_ID_LENGTH:
        raise FinancialHistoryQueryError(
            "A identidade do usuário excede o tamanho permitido."
        )

    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise FinancialHistoryQueryError(
            "A identidade do usuário contém caracteres inválidos."
        )

    return value


def _normalizar_limite(
    limite: Any,
) -> int:
    if isinstance(limite, bool) or not isinstance(limite, int):
        raise FinancialHistoryQueryError("O limite deve ser um número inteiro.")

    if not 1 <= limite <= MAX_HISTORY_LIMIT:
        raise FinancialHistoryQueryError(
            f"O limite deve estar entre 1 e {MAX_HISTORY_LIMIT}."
        )

    return limite


def _numero_seguro(
    value: Any,
) -> float | None:
    if value is None:
        return None

    try:
        number = float(value if not isinstance(value, Decimal) else str(value))
    except (
        TypeError,
        ValueError,
    ):
        return None

    if not isfinite(number):
        return None

    return round(number, 4)


def _inteiro_seguro(
    value: Any,
) -> int | None:
    if value is None:
        return None

    try:
        return int(value)
    except (
        TypeError,
        ValueError,
    ):
        return None


def _data_segura(
    value: Any,
) -> str | None:
    if isinstance(
        value,
        (datetime, date),
    ):
        return value.isoformat()

    if value is None:
        return None

    normalized = str(value).strip()

    return normalized[:40] or None


def _texto_seguro(
    value: Any,
    *,
    max_length: int,
) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()

    return normalized[:max_length] if normalized else None


def _converter_registro(
    registro: Any,
) -> dict[str, Any]:
    row = dict(registro or {})

    # Allowlist explícita. Campos como nome,
    # objetivo, diagnóstico e plano de 30 dias
    # nunca entram no resultado desta consulta.
    return {
        "data_hora": _data_segura(row.get("data_hora")),
        "saldo_estimado": _numero_seguro(row.get("saldo_estimado")),
        ("comprometimento_renda_percentual"): _numero_seguro(
            row.get("comprometimento_renda_percentual")
        ),
        "meses_reserva_estimados": (_numero_seguro(row.get("meses_reserva_estimados"))),
        "score_financeiro": (_inteiro_seguro(row.get("score_financeiro"))),
        "nivel_risco": _texto_seguro(
            row.get("nivel_risco"),
            max_length=30,
        ),
        "moeda": _texto_seguro(
            row.get("moeda"),
            max_length=20,
        ),
        "idioma": _texto_seguro(
            row.get("idioma"),
            max_length=20,
        ),
    }


def consultar_historico_financeiro_usuario(
    usuario_id: str,
    *,
    limite: int = DEFAULT_HISTORY_LIMIT,
) -> dict[str, Any]:
    """
    Consulta somente os diagnósticos vinculados à
    identidade confiável recebida pela aplicação.

    Registros legados com usuario_id NULL não são
    retornados.
    """
    normalized_user_id = _normalizar_usuario_id(usuario_id)

    normalized_limit = _normalizar_limite(limite)

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=False,
        ) as cursor:
            # Defesa em profundidade: mesmo uma
            # alteração acidental do SQL não poderá
            # escrever nesta transação.
            cursor.execute("SET TRANSACTION READ ONLY;")

            cursor.execute("SET LOCAL statement_timeout = '5000ms';")

            cursor.execute(
                SQL_CONSULTAR_HISTORICO_FINANCEIRO,
                (
                    normalized_user_id,
                    normalized_limit,
                ),
            )

            registros = cursor.fetchall() or []

    except Exception as exc:
        raise (
            FinancialHistoryRepositoryError(
                "Não foi possível consultar o histórico financeiro."
            )
        ) from exc

    diagnosticos = [_converter_registro(registro) for registro in registros]

    return {
        "possui_historico": bool(diagnosticos),
        "total_retornado": len(diagnosticos),
        "diagnosticos": diagnosticos,
    }


__all__ = [
    "DEFAULT_HISTORY_LIMIT",
    "MAX_HISTORY_LIMIT",
    "SQL_CONSULTAR_HISTORICO_FINANCEIRO",
    "FinancialHistoryQueryError",
    "FinancialHistoryRepositoryError",
    "consultar_historico_financeiro_usuario",
]
