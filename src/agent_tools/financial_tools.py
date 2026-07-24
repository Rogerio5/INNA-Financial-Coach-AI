"""
Ferramentas financeiras determinísticas da INNA.

Este módulo adapta o motor financeiro existente para o
núcleo formal de Tool Calling, sem delegar cálculos ao LLM.
"""

from __future__ import annotations

from math import isclose
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from src.agent_tools.core import (
    ToolDefinition,
    ToolExecutionContext,
)
from src.financial_engine import (
    build_financial_diagnosis,
)
from src.tools.budget_tool import (
    analisar_orcamento,
)


FINANCIAL_DIAGNOSIS_TOOL_NAME = (
    "calcular_diagnostico_financeiro"
)

MAX_MONETARY_VALUE = 1_000_000_000_000.0


class FinancialToolInvariantError(
    RuntimeError
):
    """
    Indica divergência entre os motores determinísticos.
    """


class CalcularDiagnosticoFinanceiroInput(
    BaseModel
):
    """
    Dados financeiros validados antes do cálculo.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        allow_inf_nan=False,
    )

    renda_mensal: float = Field(
        ge=0,
        le=MAX_MONETARY_VALUE,
    )

    gastos_fixos: float = Field(
        ge=0,
        le=MAX_MONETARY_VALUE,
    )

    gastos_variaveis: float = Field(
        ge=0,
        le=MAX_MONETARY_VALUE,
    )

    dividas_mensais: float = Field(
        default=0,
        ge=0,
        le=MAX_MONETARY_VALUE,
    )

    reserva_atual: float = Field(
        default=0,
        ge=0,
        le=MAX_MONETARY_VALUE,
    )

    gastos_incluem_dividas: bool = False

    moeda: str = Field(
        default="BRL",
        min_length=3,
        max_length=3,
        pattern=r"^[A-Z]{3}$",
    )

    idioma: str = Field(
        default="pt",
        min_length=2,
        max_length=10,
        pattern=(
            r"^[A-Za-z]{2,3}"
            r"(?:-[A-Za-z]{2})?$"
        ),
    )

    @field_validator(
        "moeda",
        mode="before",
    )
    @classmethod
    def normalize_currency(
        cls,
        value,
    ) -> str:
        return str(
            value or "BRL"
        ).strip().upper()


class CalcularDiagnosticoFinanceiroOutput(
    BaseModel
):
    """
    Resultado técnico e determinístico.

    O texto legado que possui moeda fixa não é exposto.
    A explicação localizada será feita em outra camada.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )

    renda_mensal: float
    gastos_fixos: float
    gastos_variaveis: float
    dividas_mensais: float
    reserva_atual: float

    moeda: str
    idioma: str

    gastos_incluem_dividas: bool

    despesas_totais: float
    saldo_estimado: float

    comprometimento_renda_percentual: float
    meses_reserva_estimados: float

    score_financeiro: int = Field(
        ge=0,
        le=100,
    )

    nivel_risco: Literal[
        "Baixo",
        "Medio",
        "Alto",
    ]

    situacao: Literal[
        "sem_renda_informada",
        "deficit",
        "equilibrio_sem_margem",
        "saldo_positivo",
    ]

    tem_saldo_positivo: bool

    parcelas_adicionais_consideradas: float
    base_calculo: str

    versao_regra: str = (
        "financial_engine_v1+budget_tool_v1"
    )


def executar_calculo_diagnostico_financeiro(
    payload: CalcularDiagnosticoFinanceiroInput,
    context: ToolExecutionContext,
) -> CalcularDiagnosticoFinanceiroOutput:
    """
    Combina os dois motores financeiros existentes.

    budget_tool:
    - resolve se a dívida já está incluída nos gastos;
    - calcula despesas, saldo e comprometimento.

    financial_engine:
    - calcula meses de reserva;
    - calcula score e risco financeiro.
    """
    del context

    gastos_mensais = (
        payload.gastos_fixos
        + payload.gastos_variaveis
    )

    orcamento = analisar_orcamento(
        renda_mensal=payload.renda_mensal,
        gastos_mensais=gastos_mensais,
        dividas_mensais=(
            payload.dividas_mensais
        ),
        gastos_incluem_dividas=(
            payload.gastos_incluem_dividas
        ),
    )

    # Quando os gastos já incluem dívidas, o motor de
    # diagnóstico recebe dívida zero para não duplicá-la.
    dividas_para_diagnostico = (
        0.0
        if payload.gastos_incluem_dividas
        else payload.dividas_mensais
    )

    diagnostico = build_financial_diagnosis({
        "renda_mensal": (
            payload.renda_mensal
        ),
        "gastos_fixos": (
            payload.gastos_fixos
        ),
        "gastos_variaveis": (
            payload.gastos_variaveis
        ),
        "dividas_mensais": (
            dividas_para_diagnostico
        ),
        "reserva_atual": (
            payload.reserva_atual
        ),
    })

    saldo_orcamento = float(
        orcamento["saldo_mensal"]
    )

    saldo_diagnostico = float(
        diagnostico["saldo_estimado"]
    )

    if not isclose(
        saldo_orcamento,
        saldo_diagnostico,
        abs_tol=0.01,
    ):
        raise FinancialToolInvariantError(
            "financial_balance_mismatch"
        )

    compromisso_orcamento = float(
        orcamento[
            "renda_comprometida_percentual"
        ]
    )

    compromisso_diagnostico = float(
        diagnostico[
            "comprometimento_renda_percentual"
        ]
    )

    if not isclose(
        compromisso_orcamento,
        compromisso_diagnostico,
        abs_tol=0.01,
    ):
        raise FinancialToolInvariantError(
            "financial_commitment_mismatch"
        )

    return CalcularDiagnosticoFinanceiroOutput(
        renda_mensal=round(
            payload.renda_mensal,
            2,
        ),
        gastos_fixos=round(
            payload.gastos_fixos,
            2,
        ),
        gastos_variaveis=round(
            payload.gastos_variaveis,
            2,
        ),
        dividas_mensais=round(
            payload.dividas_mensais,
            2,
        ),
        reserva_atual=round(
            payload.reserva_atual,
            2,
        ),
        moeda=payload.moeda,
        idioma=payload.idioma,
        gastos_incluem_dividas=(
            payload.gastos_incluem_dividas
        ),
        despesas_totais=float(
            orcamento["despesas_totais"]
        ),
        saldo_estimado=saldo_diagnostico,
        comprometimento_renda_percentual=(
            compromisso_diagnostico
        ),
        meses_reserva_estimados=float(
            diagnostico[
                "meses_reserva_estimados"
            ]
        ),
        score_financeiro=int(
            diagnostico[
                "score_financeiro"
            ]
        ),
        nivel_risco=str(
            diagnostico["nivel_risco"]
        ),
        situacao=str(
            orcamento["situacao"]
        ),
        tem_saldo_positivo=bool(
            orcamento[
                "tem_saldo_positivo"
            ]
        ),
        parcelas_adicionais_consideradas=float(
            orcamento[
                "parcelas_adicionais_consideradas"
            ]
        ),
        base_calculo=str(
            orcamento["base_calculo"]
        ),
    )


def criar_definicao_calcular_diagnostico_financeiro(
    *,
    timeout_seconds: float = 2.0,
) -> ToolDefinition:
    """
    Cria a definição registrada da ferramenta.
    """
    return ToolDefinition(
        name=(
            FINANCIAL_DIAGNOSIS_TOOL_NAME
        ),
        description=(
            "Calcula de forma determinística "
            "despesas totais, saldo mensal, "
            "comprometimento da renda, reserva, "
            "score e risco financeiro."
        ),
        input_model=(
            CalcularDiagnosticoFinanceiroInput
        ),
        output_model=(
            CalcularDiagnosticoFinanceiroOutput
        ),
        handler=(
            executar_calculo_diagnostico_financeiro
        ),
        allowed_agents=frozenset({
            "financial_agent",
        }),
        timeout_seconds=timeout_seconds,
        idempotent=True,
        sensitive_output=True,
        tags=frozenset({
            "financial",
            "deterministic",
            "calculation",
            "read_only",
        }),
    )


__all__ = [
    "CalcularDiagnosticoFinanceiroInput",
    "CalcularDiagnosticoFinanceiroOutput",
    "FINANCIAL_DIAGNOSIS_TOOL_NAME",
    "FinancialToolInvariantError",
    "criar_definicao_calcular_diagnostico_financeiro",
    "executar_calculo_diagnostico_financeiro",
]
