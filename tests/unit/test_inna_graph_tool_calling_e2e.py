from __future__ import annotations

import ast
from pathlib import Path
from unittest.mock import patch

from src.agent_tools.core import (
    ToolError,
    ToolResult,
    ToolStatus,
)
from src.agent_tools.rag_tools import (
    RAG_TOOL_NAME,
)
from src.agents.graph import (
    executar_nucleo_inna,
)


EXPLICIT_RAG_MESSAGE = (
    "Consulte a base de conhecimento RAG da INNA "
    "e responda como criar uma reserva financeira."
)


def _success_tool_result() -> ToolResult:
    return ToolResult(
        call_id="e2e-rag-success",
        tool_name=RAG_TOOL_NAME,
        status=ToolStatus.SUCCESS,
        output={
            "pergunta": EXPLICIT_RAG_MESSAGE,
            "idioma": "pt",
            "resposta": (
                "Comece definindo uma meta de reserva "
                "e separe uma parte da renda mensal."
            ),
            "fontes": [
                "guia_reserva_financeira.md",
            ],
            "modo": ("rag_hibrido_pgvector_text_neon_rerank"),
            "documentos_recuperados": 3,
            "duracao_rag_ms": 90,
        },
        duration_ms=105.0,
    )


def test_graph_routes_explicit_rag_request_through_tool_runtime():
    captured_calls = []

    def fake_execute(call):
        captured_calls.append(call)
        return _success_tool_result()

    with patch(
        "src.agents.nodes.executar_ferramenta_inna",
        side_effect=fake_execute,
    ):
        result = executar_nucleo_inna(
            EXPLICIT_RAG_MESSAGE,
            usuario_id="user-e2e",
            idioma="pt",
            moeda="BRL",
        )

    assert len(captured_calls) == 1

    call = captured_calls[0]

    assert call.tool_name == RAG_TOOL_NAME

    assert call.context.requested_by == "rag_agent"

    assert call.context.user_id == "user-e2e"

    assert call.arguments["pergunta"] == EXPLICIT_RAG_MESSAGE

    assert call.arguments["idioma"] == "pt"
    assert call.arguments["top_k"] == 4

    assert result["response"].startswith("Comece definindo")

    assert "tool:buscar_conhecimento_rag:success" in result["trace"]

    assert "agent:rag_agent" in result["trace"]

    tool_result = result["tool_results"][0]

    assert tool_result["status"] == "success"
    assert tool_result["ok"] is True

    # O estado técnico mantém apenas metadados compactos.
    assert "output" not in tool_result
    assert "resposta" not in tool_result

    rag_execution = result["structured_response"]["rag_execution"]

    assert rag_execution["retrieved_documents"] == 3

    assert rag_execution["sources"] == ["guia_reserva_financeira.md"]


def test_graph_handles_rag_tool_timeout_safely():
    timeout_result = ToolResult(
        call_id="e2e-rag-timeout",
        tool_name=RAG_TOOL_NAME,
        status=ToolStatus.TIMEOUT,
        output=None,
        error=ToolError(
            code="tool_timeout",
            message=("A ferramenta excedeu o tempo máximo de execução."),
            retryable=True,
            details={
                "timeout_seconds": 20.0,
            },
        ),
        duration_ms=20000.0,
    )

    with patch(
        "src.agents.nodes.executar_ferramenta_inna",
        return_value=timeout_result,
    ):
        result = executar_nucleo_inna(
            EXPLICIT_RAG_MESSAGE,
            usuario_id="user-e2e",
            idioma="pt",
            moeda="BRL",
        )

    assert result["response"] == (
        "Não foi possível consultar a base de conhecimento neste momento."
    )

    stored_result = result["tool_results"][0]

    assert stored_result["status"] == "timeout"

    assert stored_result["error_code"] == "tool_timeout"

    assert stored_result["retryable"] is True

    assert "tool:buscar_conhecimento_rag:timeout" in result["trace"]

    assert "agent:rag_agent:error" in result["trace"]

    assert result["errors"] == [("A ferramenta excedeu o tempo máximo de execução.")]


def test_agent_nodes_cannot_call_legacy_rag_directly():
    """
    Teste de arquitetura.

    Protege a fronteira de Tool Calling e impede
    regressões para chamadas diretas ao RAG legado.
    """
    source_path = Path("src/agents/nodes.py")

    source = source_path.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(source)

    imported_names: set[str] = set()
    called_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.add(alias.asname or alias.name)

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.add(node.func.id)

            elif isinstance(
                node.func,
                ast.Attribute,
            ):
                called_names.add(node.func.attr)

    assert "consultar_rag_inna" not in imported_names

    assert "consultar_rag_inna" not in called_names

    assert "executar_ferramenta_inna" in imported_names

    assert "executar_ferramenta_inna" in called_names

    assert "ToolCall" in imported_names
    assert "ToolCall" in called_names
