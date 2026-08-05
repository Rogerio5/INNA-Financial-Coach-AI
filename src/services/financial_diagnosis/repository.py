from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from src.database.connection import (
    cursor_postgres,
)

from .contracts import (
    FinancialDiagnosisPersistenceCommand,
)


SQL_INSERT_DIAGNOSTICO = """
INSERT INTO public.diagnosticos_financeiros (
    usuario_id,
    idempotency_key,
    request_fingerprint,
    data_hora,
    nome,
    renda_mensal,
    gastos_fixos,
    gastos_variaveis,
    dividas_mensais,
    reserva_atual,
    objetivo,
    idioma,
    moeda,
    simbolo_moeda,
    saldo_estimado,
    comprometimento_renda_percentual,
    meses_reserva_estimados,
    score_financeiro,
    nivel_risco,
    diagnostico,
    plano_30_dias
)
VALUES (
    %(usuario_id)s,
    %(idempotency_key)s,
    %(request_fingerprint)s,
    NOW(),
    %(nome)s,
    %(renda_mensal)s,
    %(gastos_fixos)s,
    %(gastos_variaveis)s,
    %(dividas_mensais)s,
    %(reserva_atual)s,
    %(objetivo)s,
    %(idioma)s,
    %(moeda)s,
    %(simbolo_moeda)s,
    %(saldo_estimado)s,
    %(comprometimento_renda_percentual)s,
    %(meses_reserva_estimados)s,
    %(score_financeiro)s,
    %(nivel_risco)s,
    %(diagnostico)s,
    %(plano_30_dias)s
)
ON CONFLICT (
    usuario_id,
    idempotency_key
)
WHERE
    usuario_id IS NOT NULL
    AND idempotency_key IS NOT NULL
DO NOTHING
RETURNING
    id,
    data_hora,
    request_fingerprint;
"""


SQL_CONSULTAR_IDEMPOTENCIA = """
SELECT
    id,
    data_hora,
    request_fingerprint
FROM public.diagnosticos_financeiros
WHERE
    usuario_id = %(usuario_id)s
    AND idempotency_key =
        %(idempotency_key)s
LIMIT 1;
"""


class FinancialDiagnosisRepositoryError(RuntimeError):
    """
    Falha sanitizada na persistência do diagnóstico.
    """


class IdempotencyConflictError(FinancialDiagnosisRepositoryError):
    """
    A mesma chave foi reutilizada com conteúdo
    financeiro diferente.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class FinancialDiagnosisWriteResult:
    id: int
    status: Literal[
        "created",
        "existing",
    ]
    data_hora: datetime

    @property
    def created(
        self,
    ) -> bool:
        return self.status == "created"

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status,
            "created": self.created,
            "data_hora": self.data_hora,
        }


def _montar_parametros(
    command: FinancialDiagnosisPersistenceCommand,
) -> dict[str, Any]:
    """
    Monta uma allowlist explícita.

    Campos adicionados futuramente aos modelos não
    serão persistidos automaticamente.
    """
    context = command.context
    diagnosis = command.diagnosis

    return {
        "usuario_id": context.usuario_id,
        "idempotency_key": (context.idempotency_key),
        "request_fingerprint": (command.request_fingerprint),
        "nome": diagnosis.nome,
        "renda_mensal": (diagnosis.renda_mensal),
        "gastos_fixos": (diagnosis.gastos_fixos),
        "gastos_variaveis": (diagnosis.gastos_variaveis),
        "dividas_mensais": (diagnosis.dividas_mensais),
        "reserva_atual": (diagnosis.reserva_atual),
        "objetivo": diagnosis.objetivo,
        "idioma": diagnosis.idioma,
        "moeda": diagnosis.moeda,
        "simbolo_moeda": (diagnosis.simbolo_moeda),
        "saldo_estimado": (diagnosis.saldo_estimado),
        ("comprometimento_renda_percentual"): (
            diagnosis.comprometimento_renda_percentual
        ),
        "meses_reserva_estimados": (diagnosis.meses_reserva_estimados),
        "score_financeiro": (diagnosis.score_financeiro),
        "nivel_risco": (diagnosis.nivel_risco),
        "diagnostico": (diagnosis.diagnostico),
        "plano_30_dias": (diagnosis.plano_30_dias),
    }


def _extrair_resultado(
    registro: Mapping[str, Any],
    *,
    status: Literal[
        "created",
        "existing",
    ],
) -> FinancialDiagnosisWriteResult:
    try:
        raw_id = registro["id"]
        data_hora = registro["data_hora"]
    except (
        KeyError,
        TypeError,
    ):
        raise FinancialDiagnosisRepositoryError(
            "O banco retornou um registro de diagnóstico inválido."
        ) from None

    if isinstance(raw_id, bool) or not isinstance(raw_id, int) or raw_id < 1:
        raise FinancialDiagnosisRepositoryError(
            "O banco retornou um identificador de diagnóstico inválido."
        )

    if not isinstance(
        data_hora,
        datetime,
    ):
        raise FinancialDiagnosisRepositoryError(
            "O banco retornou uma data de diagnóstico inválida."
        )

    return FinancialDiagnosisWriteResult(
        id=raw_id,
        status=status,
        data_hora=data_hora,
    )


def _fingerprint_do_registro(
    registro: Mapping[str, Any],
) -> str:
    try:
        value = registro["request_fingerprint"]
    except (
        KeyError,
        TypeError,
    ):
        raise FinancialDiagnosisRepositoryError(
            "O banco não retornou o fingerprint do diagnóstico."
        ) from None

    if not isinstance(value, str) or len(value) != 64:
        raise FinancialDiagnosisRepositoryError(
            "O banco retornou um fingerprint de diagnóstico inválido."
        )

    return value


def salvar_diagnostico_financeiro(
    command: FinancialDiagnosisPersistenceCommand,
) -> FinancialDiagnosisWriteResult:
    """
    Persiste um diagnóstico de maneira idempotente.

    Retornos:
    - created: um novo registro foi criado;
    - existing: a mesma chave e o mesmo conteúdo
      já haviam sido persistidos.

    A reutilização da chave com conteúdo diferente
    gera IdempotencyConflictError.
    """
    if not isinstance(
        command,
        FinancialDiagnosisPersistenceCommand,
    ):
        raise TypeError(
            "command deve ser uma instância de FinancialDiagnosisPersistenceCommand."
        )

    parameters = _montar_parametros(command)

    expected_fingerprint = parameters["request_fingerprint"]

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            cursor.execute("SET LOCAL lock_timeout = '3000ms';")

            cursor.execute("SET LOCAL statement_timeout = '5000ms';")

            cursor.execute(
                SQL_INSERT_DIAGNOSTICO,
                parameters,
            )

            inserted = cursor.fetchone()

            if inserted is not None:
                inserted_fingerprint = _fingerprint_do_registro(inserted)

                if inserted_fingerprint != expected_fingerprint:
                    raise (
                        FinancialDiagnosisRepositoryError(
                            "O banco retornou um fingerprint inesperado."
                        )
                    )

                return _extrair_resultado(
                    inserted,
                    status="created",
                )

            cursor.execute(
                SQL_CONSULTAR_IDEMPOTENCIA,
                {
                    "usuario_id": (command.context.usuario_id),
                    "idempotency_key": (command.context.idempotency_key),
                },
            )

            existing = cursor.fetchone()

            if existing is None:
                raise (
                    FinancialDiagnosisRepositoryError(
                        "Não foi possível localizar "
                        "o diagnóstico após o "
                        "conflito de idempotência."
                    )
                )

            existing_fingerprint = _fingerprint_do_registro(existing)

            if existing_fingerprint != expected_fingerprint:
                raise IdempotencyConflictError(
                    "A chave de idempotência já "
                    "foi utilizada com outro "
                    "conteúdo financeiro."
                )

            return _extrair_resultado(
                existing,
                status="existing",
            )

    except IdempotencyConflictError:
        raise

    except FinancialDiagnosisRepositoryError:
        raise

    except Exception:
        raise FinancialDiagnosisRepositoryError(
            "Não foi possível persistir o diagnóstico financeiro."
        ) from None


__all__ = [
    "FinancialDiagnosisRepositoryError",
    "FinancialDiagnosisWriteResult",
    "IdempotencyConflictError",
    "SQL_CONSULTAR_IDEMPOTENCIA",
    "SQL_INSERT_DIAGNOSTICO",
    "salvar_diagnostico_financeiro",
]
