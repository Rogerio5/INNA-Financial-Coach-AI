"""Servidor MCP governado da INNA.

Fluxo:
MCP -> ToolCall -> ToolPermissionPolicy -> ToolExecutor -> ferramenta.

As regras de RAG e diagnóstico financeiro não são duplicadas.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from mcp.server import MCPServer

from src.agent_tools.core.contracts import (
    ToolCall,
    ToolExecutionContext,
)
from src.agent_tools.runtime import (
    executar_ferramenta_inna,
)
from src.mcp_server.audit import (
    hash_arguments,
    registrar_evento_mcp,
)
from src.mcp_server.security import (
    validar_autenticacao_interna,
)


SERVER_NAME = "inna-mcp-level-2"
SERVER_VERSION = "0.3.0"

_TOOL_AGENT_MAPPING = {
    "buscar_conhecimento_rag": "rag_agent",
    "calcular_diagnostico_financeiro": "financial_agent",
    "preparar_email_financeiro": "communication_agent",
    "preparar_mensagem_telegram": "communication_agent",
}


class MCPToolExecutionError(RuntimeError):
    """Erro seguro retornado pela camada MCP."""


def _novo_trace_id() -> str:
    return f"mcp-{uuid4().hex}"


def _executar_tool_governada(
    *,
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Executa ferramenta pelo runtime oficial da INNA."""

    validar_autenticacao_interna()

    requested_by = _TOOL_AGENT_MAPPING.get(tool_name)

    if requested_by is None:
        raise MCPToolExecutionError(f"Ferramenta MCP não autorizada: {tool_name}")

    trace_id = _novo_trace_id()

    context = ToolExecutionContext(
        requested_by=requested_by,
        trace_id=trace_id,
        metadata={
            "source": "mcp",
            "server": SERVER_NAME,
            "server_version": SERVER_VERSION,
            "tool_name": tool_name,
            "transport_scope": "internal",
        },
    )

    call = ToolCall(
        tool_name=tool_name,
        arguments=arguments,
        context=context,
    )

    result = executar_ferramenta_inna(
        call,
    )

    arguments_hash = hash_arguments(arguments)

    if result.output is not None:
        registrar_evento_mcp(
            call_id=result.call_id,
            trace_id=trace_id,
            tool_name=result.tool_name,
            status="success",
            duration_ms=result.duration_ms,
            arguments_hash=arguments_hash,
        )

        return {
            **result.output,
            "_mcp": {
                "call_id": result.call_id,
                "trace_id": trace_id,
                "tool_name": result.tool_name,
                "status": str(
                    getattr(
                        result.status,
                        "value",
                        result.status,
                    )
                ),
                "duration_ms": result.duration_ms,
                "server": SERVER_NAME,
                "server_version": SERVER_VERSION,
            },
        }

    error_code = "tool_execution_failed"
    error_message = "A ferramenta não pôde ser executada."

    if result.error is not None:
        error_code = getattr(
            result.error,
            "code",
            error_code,
        )

        safe_message = getattr(
            result.error,
            "message",
            None,
        )

        if safe_message:
            error_message = safe_message

    registrar_evento_mcp(
        call_id=result.call_id,
        trace_id=trace_id,
        tool_name=result.tool_name,
        status="error",
        duration_ms=result.duration_ms,
        arguments_hash=arguments_hash,
        error_code=error_code,
    )

    raise MCPToolExecutionError(f"{error_code}: {error_message}")


def buscar_conhecimento_rag(
    pergunta: str,
    idioma: str = "pt",
    top_k: int = 4,
) -> dict[str, Any]:
    """Busca conhecimento na base RAG híbrida da INNA."""

    return _executar_tool_governada(
        tool_name="buscar_conhecimento_rag",
        arguments={
            "pergunta": pergunta,
            "idioma": idioma,
            "top_k": top_k,
        },
    )


def calcular_diagnostico_financeiro(
    renda_mensal: float,
    gastos_fixos: float,
    gastos_variaveis: float,
    dividas_mensais: float = 0,
    reserva_atual: float = 0,
    gastos_incluem_dividas: bool = False,
    moeda: str = "BRL",
    idioma: str = "pt",
) -> dict[str, Any]:
    """Calcula diagnóstico pelo motor financeiro oficial."""

    return _executar_tool_governada(
        tool_name="calcular_diagnostico_financeiro",
        arguments={
            "renda_mensal": renda_mensal,
            "gastos_fixos": gastos_fixos,
            "gastos_variaveis": gastos_variaveis,
            "dividas_mensais": dividas_mensais,
            "reserva_atual": reserva_atual,
            "gastos_incluem_dividas": (gastos_incluem_dividas),
            "moeda": moeda,
            "idioma": idioma,
        },
    )


def preparar_email_financeiro(
    destinatario: str,
    assunto: str,
    corpo: str,
    html_corpo: str | None = None,
    idioma: str = "pt",
) -> dict[str, Any]:
    """
    Prepara um e-mail para aprovação humana.

    Esta ferramenta não envia o e-mail.
    """
    return _executar_tool_governada(
        tool_name="preparar_email_financeiro",
        arguments={
            "destinatario": destinatario,
            "assunto": assunto,
            "corpo": corpo,
            "html_corpo": html_corpo,
            "idioma": idioma,
        },
    )


def preparar_mensagem_telegram(
    chat_id: str,
    mensagem: str,
    idioma: str = "pt",
) -> dict[str, Any]:
    """
    Prepara uma mensagem Telegram para aprovação humana.

    Esta ferramenta não envia a mensagem.
    """
    return _executar_tool_governada(
        tool_name="preparar_mensagem_telegram",
        arguments={
            "chat_id": chat_id,
            "mensagem": mensagem,
            "idioma": idioma,
        },
    )


def criar_servidor_mcp_inna() -> MCPServer:
    """Cria servidor MCP governado da INNA."""

    mcp_server = MCPServer(
        name=SERVER_NAME,
        title="INNA Governed MCP Server",
        description=(
            "Servidor MCP interno com validação, permissões, "
            "rastreamento e execução pelo runtime oficial."
        ),
        instructions=(
            "Utilize somente ferramentas registradas e autorizadas. "
            "Identidade, permissões e contexto são definidos no servidor."
        ),
        version=SERVER_VERSION,
        warn_on_duplicate_tools=True,
        log_level="INFO",
    )

    mcp_server.add_tool(
        buscar_conhecimento_rag,
        name="buscar_conhecimento_rag",
        title="Buscar conhecimento RAG",
        description=(
            "Consulta a base RAG híbrida da INNA utilizando "
            "permissões e execução governada."
        ),
        structured_output=True,
    )

    mcp_server.add_tool(
        calcular_diagnostico_financeiro,
        name="calcular_diagnostico_financeiro",
        title="Calcular diagnóstico financeiro",
        description=(
            "Executa o motor financeiro determinístico da INNA "
            "por meio do runtime governado."
        ),
        structured_output=True,
    )

    mcp_server.add_tool(
        preparar_email_financeiro,
        name="preparar_email_financeiro",
        title="Preparar e-mail financeiro",
        description=(
            "Prepara e valida um e-mail financeiro para aprovação humana. Não envia."
        ),
        structured_output=True,
    )

    mcp_server.add_tool(
        preparar_mensagem_telegram,
        name="preparar_mensagem_telegram",
        title="Preparar mensagem Telegram",
        description=(
            "Prepara e valida uma mensagem Telegram para aprovação humana. Não envia."
        ),
        structured_output=True,
    )

    return mcp_server


server = criar_servidor_mcp_inna()


def main() -> None:
    server.run(
        transport="stdio",
    )


if __name__ == "__main__":
    main()
