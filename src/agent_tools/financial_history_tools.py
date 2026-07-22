"""
Ferramenta formal de consulta ao histórico financeiro.

A identidade do usuário nunca é recebida nos argumentos
gerados pelo modelo. Ela vem exclusivamente do
ToolExecutionContext criado pela aplicação.
"""

from __future__ import annotations

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
from src.services.financial_history.repository import (
    DEFAULT_HISTORY_LIMIT,
    MAX_HISTORY_LIMIT,
    FinancialHistoryQueryError,
    FinancialHistoryRepositoryError,
    consultar_historico_financeiro_usuario,
)


FINANCIAL_HISTORY_TOOL_NAME = (
    "consultar_historico_financeiro"
)


class ConsultarHistoricoFinanceiroInput(
    BaseModel
):
    """
    Argumentos públicos enviados pelo agente.

    usuario_id e nome não fazem parte deste contrato.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    limite: int = Field(
        default=DEFAULT_HISTORY_LIMIT,
        ge=1,
        le=MAX_HISTORY_LIMIT,
        description=(
            "Quantidade máxima de diagnósticos "
            "recentes a consultar."
        ),
    )


class HistoricoFinanceiroItem(
    BaseModel
):
    """Registro financeiro mínimo e permitido."""

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


class ConsultarHistoricoFinanceiroOutput(
    BaseModel
):
    """Saída validada da ferramenta."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    possui_historico: bool

    total_retornado: int = Field(
        ge=0,
        le=MAX_HISTORY_LIMIT,
    )

    diagnosticos: list[
        HistoricoFinanceiroItem
    ] = Field(
        default_factory=list,
        max_length=MAX_HISTORY_LIMIT,
    )

    @model_validator(
        mode="after"
    )
    def validar_consistencia(
        self,
    ):
        total_real = len(
            self.diagnosticos
        )

        if self.total_retornado != total_real:
            raise ValueError(
                "total_retornado não corresponde "
                "à quantidade de diagnósticos."
            )

        if self.possui_historico != (
            total_real > 0
        ):
            raise ValueError(
                "possui_historico está inconsistente."
            )

        return self


class FinancialHistoryToolExecutionError(
    RuntimeError
):
    """Falha interna e segura da ferramenta."""


def executar_consulta_historico_financeiro(
    payload: ConsultarHistoricoFinanceiroInput,
    context: ToolExecutionContext,
) -> ConsultarHistoricoFinanceiroOutput:
    """
    Executa a consulta utilizando exclusivamente
    a identidade confiável do contexto.
    """
    trusted_user_id = str(
        context.user_id or ""
    ).strip()

    if not trusted_user_id:
        raise FinancialHistoryToolExecutionError(
            "missing_trusted_user_identity"
        )

    try:
        result = (
            consultar_historico_financeiro_usuario(
                trusted_user_id,
                limite=payload.limite,
            )
        )

    except (
        FinancialHistoryQueryError,
        FinancialHistoryRepositoryError,
    ) as exc:
        raise FinancialHistoryToolExecutionError(
            type(exc).__name__
        ) from exc

    return (
        ConsultarHistoricoFinanceiroOutput(
            **result
        )
    )


def criar_definicao_consultar_historico_financeiro(
    *,
    timeout_seconds: float = 5.0,
) -> ToolDefinition:
    """Cria a definição formal da ferramenta."""
    return ToolDefinition(
        name=FINANCIAL_HISTORY_TOOL_NAME,
        description=(
            "Consulta os diagnósticos financeiros "
            "recentes do usuário autenticado. "
            "A identidade é obtida exclusivamente "
            "do contexto confiável da aplicação."
        ),
        input_model=(
            ConsultarHistoricoFinanceiroInput
        ),
        output_model=(
            ConsultarHistoricoFinanceiroOutput
        ),
        handler=(
            executar_consulta_historico_financeiro
        ),
        allowed_agents=frozenset({
            "financial_agent",
            "report_agent",
        }),
        timeout_seconds=timeout_seconds,
        idempotent=True,
        sensitive_output=True,
        tags=frozenset({
            "financial_history",
            "postgresql",
            "read_only",
            "user_scoped",
        }),
    )


__all__ = [
    "FINANCIAL_HISTORY_TOOL_NAME",
    "ConsultarHistoricoFinanceiroInput",
    "ConsultarHistoricoFinanceiroOutput",
    "HistoricoFinanceiroItem",
    "FinancialHistoryToolExecutionError",
    "criar_definicao_consultar_historico_financeiro",
    "executar_consulta_historico_financeiro",
]
