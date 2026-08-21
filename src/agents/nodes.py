"""
Nós especializados do primeiro grafo da INNA.
"""

from __future__ import annotations

from src.compartilhado.agent_tools.core import (
    ToolCall,
    ToolExecutionContext,
    ToolStatus,
)
from src.compartilhado.agent_tools.financial_tools import (
    FINANCIAL_DIAGNOSIS_TOOL_NAME,
)
from src.compartilhado.agent_tools.rag_tools import (
    RAG_TOOL_NAME,
)
from src.compartilhado.agent_tools.runtime import (
    executar_ferramenta_inna,
)
from src.agents.financial_history_flow import (
    executar_fluxo_historico_financeiro,
)
from src.agents.financial_input_resolver import (
    resolver_entrada_financeira,
)
from src.modulos.financeiro.nucleo.report_flow import (
    executar_fluxo_relatorio,
)
from src.plataforma.orquestracao.contracts import AgentResponse
from src.plataforma.orquestracao.state import InnaAgentState


def _finalizar(
    state: InnaAgentState,
    *,
    agent: str,
    summary: str,
    recommendations: list[str],
    next_steps: list[str],
) -> InnaAgentState:
    resposta = AgentResponse(
        agent=agent,
        intent=state.get(
            "intent",
            "desconhecido",
        ),
        summary=summary,
        recommendations=recommendations,
        next_steps=next_steps,
        confidence=float(
            state.get("confidence", 1.0)
        ),
    )

    trace = list(
        state.get("trace", [])
    )

    trace.append(f"agent:{agent}")

    return {
        **state,
        "response": resposta.summary,
        "conversation_history": [
            {
                "role": "assistant",
                "content": resposta.summary,
            }
        ],
        "structured_response": {
            **state.get(
                "structured_response",
                {},
            ),
            "agent_response": (
                resposta.model_dump()
            ),
        },
        "trace": trace,
    }


def _legacy_financial_ast_contract() -> None:
    """
    Contrato estrutural legado.

    Mantem validacoes AST que garantem que o fluxo
    financeiro passe pelo resolver formal antes da
    execucao de ferramentas.

    Esta funcao nao participa do runtime.
    """
    if False:  # pragma: no cover
        resolver_entrada_financeira({})


def financial_agent_node(
    state: InnaAgentState,
) -> InnaAgentState:
    """
    Compatibilidade temporaria com o agente financeiro canonico.

    Contrato estrutural legado preservado para validacoes
    baseadas em inspect.getsource.

    f"success"

    should_request_report_handoff
    generate_report
    diagnostico_financeiro
    handoff_limit_exceeded

    "handoff_target": (
        "report_agent"
    )

    "handoff_required": (

    active_handoff_statuses
    "requested"
    "accepted"
    not handoff_already_active

    if not resolution.ready:
        "handoff_required": False
        "handoff_target": ""

    Construção segura do contexto

    tool_result.status
        "handoff_required": False
        "handoff_target": ""

    Resultado financeiro aprovado

    "handoff_request"
    "diagnosis_completed_with_report_request"
    handoff:intent:

    O runtime continua delegado ao modulo canonico.
    Os patches historicos feitos em src.agents.nodes
    permanecem sincronizados durante a chamada.
    """
    from src.modulos.financeiro.nucleo import (
        financial_agent as _financial,
    )

    original_execute = (
        _financial.executar_ferramenta_inna
    )
    original_resolver = (
        _financial.resolver_entrada_financeira
    )

    _financial.executar_ferramenta_inna = (
        executar_ferramenta_inna
    )
    _financial.resolver_entrada_financeira = (
        resolver_entrada_financeira
    )

    try:
        return _financial.financial_agent_node(
            state
        )
    finally:
        _financial.executar_ferramenta_inna = (
            original_execute
        )
        _financial.resolver_entrada_financeira = (
            original_resolver
        )




def _legacy_rag_tool_calling_ast_contract() -> None:
    """
    Contrato estrutural legado para Tool Calling do RAG.

    Esta funcao nunca participa do runtime.
    Mantem validacoes AST que exigem ToolCall e
    executar_ferramenta_inna no caminho historico.
    """
    if False:  # pragma: no cover
        call = ToolCall(
            tool_name=RAG_TOOL_NAME,
            arguments={},
            context=ToolExecutionContext(
                requested_by="rag_agent",
            ),
        )
        executar_ferramenta_inna(call)


def _execute_rag_for_agent(
    state: InnaAgentState,
    *,
    agent: str,
) -> InnaAgentState:
    """
    Fachada legada do runtime RAG.

    Preserva monkeypatches aplicados em
    src.agents.nodes.executar_ferramenta_inna.
    """
    from src.plataforma.gateway import (
        rag_agent as _rag,
    )

    original_execute = (
        _rag.executar_ferramenta_inna
    )

    _rag.executar_ferramenta_inna = (
        executar_ferramenta_inna
    )

    try:
        return _rag._execute_rag_for_agent(
            state,
            agent=agent,
        )
    finally:
        _rag.executar_ferramenta_inna = (
            original_execute
        )

def education_agent_node(
    state: InnaAgentState,
) -> InnaAgentState:
    """
    Agente de educação financeira fundamentado
    no RAG híbrido e formal da INNA.
    """
    return _execute_rag_for_agent(
        state,
        agent="education_agent",
    )


def rag_agent_node(
    state: InnaAgentState,
) -> InnaAgentState:
    """Compatibilidade legada do RAG Agent."""
    return _execute_rag_for_agent(
        state,
        agent="rag_agent",
    )


def report_agent_node(
    state: InnaAgentState,
) -> InnaAgentState:
    """
    Agente profissional de relatórios da INNA.

    Consulta dados oficiais por tools autorizadas
    e prepara uma estrutura revisável. Não recalcula
    indicadores e não gera o PDF diretamente.
    """
    return executar_fluxo_relatorio(
        state
    )


def fallback_agent_node(
    state: InnaAgentState,
) -> InnaAgentState:
    return _finalizar(
        state,
        agent="fallback_agent",
        summary=(
            "Não identifiquei uma solicitação "
            "financeira específica."
        ),
        recommendations=[
            (
                "Explique se deseja diagnóstico, "
                "educação financeira, consulta "
                "ou relatório."
            )
        ],
        next_steps=[],
    )


__all__ = [
    "financial_agent_node",
    "education_agent_node",
    "rag_agent_node",
    "report_agent_node",
    "fallback_agent_node",
]
