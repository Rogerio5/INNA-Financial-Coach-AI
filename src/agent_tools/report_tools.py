"""
Ferramentas formais do agente de relatório da INNA.

A preparação do relatório:
- utiliza somente dados financeiros oficiais;
- não recalcula indicadores;
- não consulta banco ou serviços externos;
- não gera PDF diretamente;
- produz uma estrutura validada e revisável.
"""

from __future__ import annotations

from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from src.agent_tools.core import (
    ToolDefinition,
    ToolExecutionContext,
)


PREPARE_FINANCIAL_REPORT_TOOL_NAME = (
    "preparar_relatorio_financeiro"
)

MAX_REPORT_DIAGNOSES = 20
MAX_REPORT_RECOMMENDATIONS = 10
MAX_REPORT_TEXT_LENGTH = 2_000


class RelatorioDiagnosticoItem(
    BaseModel
):
    """
    Diagnóstico financeiro oficial permitido
    para composição de relatório.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    data_hora: str | None = Field(
        default=None,
        max_length=100,
    )

    saldo_estimado: float | None = None

    comprometimento_renda_percentual: (
        float | None
    ) = None

    meses_reserva_estimados: (
        float | None
    ) = None

    score_financeiro: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    nivel_risco: str | None = Field(
        default=None,
        max_length=50,
    )

    moeda: str | None = Field(
        default=None,
        max_length=10,
    )

    idioma: str | None = Field(
        default=None,
        max_length=20,
    )


class PrepararRelatorioFinanceiroInput(
    BaseModel
):
    """
    Dados oficiais fornecidos ao agente de relatório.

    A identidade do usuário nunca faz parte dos
    argumentos controlados pelo modelo.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    diagnosticos: list[
        RelatorioDiagnosticoItem
    ] = Field(
        default_factory=list,
        max_length=MAX_REPORT_DIAGNOSES,
    )

    titulo: str = Field(
        default="Relatório Financeiro INNA",
        min_length=1,
        max_length=120,
    )

    resumo_executivo: str | None = Field(
        default=None,
        max_length=MAX_REPORT_TEXT_LENGTH,
    )

    recomendacoes: list[str] = Field(
        default_factory=list,
        max_length=MAX_REPORT_RECOMMENDATIONS,
    )

    proximos_passos: list[str] = Field(
        default_factory=list,
        max_length=MAX_REPORT_RECOMMENDATIONS,
    )

    idioma: str = Field(
        default="pt",
        min_length=2,
        max_length=20,
    )

    @model_validator(mode="after")
    def validar_conteudo(
        self,
    ):
        recommendations = [
            item.strip()
            for item in self.recomendacoes
            if item.strip()
        ]

        next_steps = [
            item.strip()
            for item in self.proximos_passos
            if item.strip()
        ]

        if len(recommendations) != len(
            self.recomendacoes
        ):
            raise ValueError(
                "Recomendações vazias não são permitidas."
            )

        if len(next_steps) != len(
            self.proximos_passos
        ):
            raise ValueError(
                "Próximos passos vazios não são permitidos."
            )

        return self


class RelatorioIndicadoresOficiais(
    BaseModel
):
    """
    Indicadores copiados do diagnóstico mais recente.

    Nenhum indicador é recalculado nesta ferramenta.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    data_hora: str | None = None
    saldo_estimado: float | None = None

    comprometimento_renda_percentual: (
        float | None
    ) = None

    meses_reserva_estimados: (
        float | None
    ) = None

    score_financeiro: int | None = None
    nivel_risco: str | None = None
    moeda: str | None = None
    idioma: str | None = None


class PrepararRelatorioFinanceiroOutput(
    BaseModel
):
    """
    Estrutura final revisável antes da geração do PDF.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    report_version: str = "1.0"
    titulo: str
    idioma: str

    possui_diagnostico: bool
    total_diagnosticos: int = Field(
        ge=0,
        le=MAX_REPORT_DIAGNOSES,
    )

    indicadores_oficiais: (
        RelatorioIndicadoresOficiais | None
    ) = None

    historico: list[
        RelatorioDiagnosticoItem
    ] = Field(
        default_factory=list,
        max_length=MAX_REPORT_DIAGNOSES,
    )

    resumo_executivo: str
    recomendacoes: list[str]
    proximos_passos: list[str]

    financial_values_recalculated: bool = False
    ready_for_risk_review: bool = True
    ready_for_pdf_rendering: bool = False

    @model_validator(mode="after")
    def validar_consistencia(
        self,
    ):
        total = len(self.historico)

        if self.total_diagnosticos != total:
            raise ValueError(
                "total_diagnosticos está inconsistente."
            )

        if self.possui_diagnostico != (
            total > 0
        ):
            raise ValueError(
                "possui_diagnostico está inconsistente."
            )

        if (
            total == 0
            and self.indicadores_oficiais
            is not None
        ):
            raise ValueError(
                "Não pode haver indicadores sem diagnóstico."
            )

        if (
            total > 0
            and self.indicadores_oficiais
            is None
        ):
            raise ValueError(
                "Diagnóstico existente exige indicadores."
            )

        if self.financial_values_recalculated:
            raise ValueError(
                "O relatório não pode recalcular "
                "valores financeiros."
            )

        return self


class ReportPreparationError(
    RuntimeError
):
    """Falha segura na preparação do relatório."""


def _normalized_text(
    value: Any,
    *,
    default: str,
) -> str:
    normalized = str(
        value or ""
    ).strip()

    return normalized or default


def _default_summary(
    *,
    possui_diagnostico: bool,
    total_diagnosticos: int,
) -> str:
    if not possui_diagnostico:
        return (
            "Ainda não existem diagnósticos financeiros "
            "disponíveis para compor o relatório."
        )

    if total_diagnosticos == 1:
        return (
            "O relatório foi preparado com base no "
            "diagnóstico financeiro oficial disponível."
        )

    return (
        "O relatório foi preparado com base nos "
        f"{total_diagnosticos} diagnósticos financeiros "
        "oficiais mais recentes."
    )


def executar_preparacao_relatorio_financeiro(
    payload: PrepararRelatorioFinanceiroInput,
    context: ToolExecutionContext,
) -> PrepararRelatorioFinanceiroOutput:
    """
    Organiza os resultados oficiais sem recalculá-los.

    A identidade confiável é exigida para impedir que
    relatórios sejam preparados fora de um contexto
    autenticado.
    """
    trusted_user_id = str(
        context.user_id or ""
    ).strip()

    if not trusted_user_id:
        raise ReportPreparationError(
            "missing_trusted_user_identity"
        )

    diagnostics = list(
        payload.diagnosticos
    )

    latest = (
        diagnostics[0]
        if diagnostics
        else None
    )

    official_indicators = None

    if latest is not None:
        official_indicators = (
            RelatorioIndicadoresOficiais(
                data_hora=latest.data_hora,
                saldo_estimado=(
                    latest.saldo_estimado
                ),
                comprometimento_renda_percentual=(
                    latest
                    .comprometimento_renda_percentual
                ),
                meses_reserva_estimados=(
                    latest.meses_reserva_estimados
                ),
                score_financeiro=(
                    latest.score_financeiro
                ),
                nivel_risco=latest.nivel_risco,
                moeda=latest.moeda,
                idioma=latest.idioma,
            )
        )

    possui_diagnostico = bool(
        diagnostics
    )

    summary = _normalized_text(
        payload.resumo_executivo,
        default=_default_summary(
            possui_diagnostico=(
                possui_diagnostico
            ),
            total_diagnosticos=len(
                diagnostics
            ),
        ),
    )

    return PrepararRelatorioFinanceiroOutput(
        titulo=_normalized_text(
            payload.titulo,
            default="Relatório Financeiro INNA",
        ),
        idioma=_normalized_text(
            payload.idioma,
            default="pt",
        ),
        possui_diagnostico=(
            possui_diagnostico
        ),
        total_diagnosticos=len(
            diagnostics
        ),
        indicadores_oficiais=(
            official_indicators
        ),
        historico=diagnostics,
        resumo_executivo=summary,
        recomendacoes=list(
            payload.recomendacoes
        ),
        proximos_passos=list(
            payload.proximos_passos
        ),
        financial_values_recalculated=False,
        ready_for_risk_review=True,
        ready_for_pdf_rendering=False,
    )


def criar_definicao_preparar_relatorio_financeiro(
    *,
    timeout_seconds: float = 2.0,
) -> ToolDefinition:
    """
    Cria a definição formal da preparação do relatório.
    """
    return ToolDefinition(
        name=PREPARE_FINANCIAL_REPORT_TOOL_NAME,
        description=(
            "Organiza diagnósticos financeiros oficiais "
            "em uma estrutura de relatório. Não recalcula "
            "indicadores e não gera o PDF diretamente."
        ),
        input_model=(
            PrepararRelatorioFinanceiroInput
        ),
        output_model=(
            PrepararRelatorioFinanceiroOutput
        ),
        handler=(
            executar_preparacao_relatorio_financeiro
        ),
        allowed_agents=frozenset({
            "report_agent",
        }),
        timeout_seconds=timeout_seconds,
        idempotent=True,
        sensitive_output=True,
        tags=frozenset({
            "financial_report",
            "deterministic",
            "user_scoped",
            "no_recalculation",
            "pre_render",
        }),
    )


__all__ = [
    "PREPARE_FINANCIAL_REPORT_TOOL_NAME",
    "MAX_REPORT_DIAGNOSES",
    "MAX_REPORT_RECOMMENDATIONS",
    "RelatorioDiagnosticoItem",
    "PrepararRelatorioFinanceiroInput",
    "RelatorioIndicadoresOficiais",
    "PrepararRelatorioFinanceiroOutput",
    "ReportPreparationError",
    "executar_preparacao_relatorio_financeiro",
    "criar_definicao_preparar_relatorio_financeiro",
]
