from __future__ import annotations

from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.agent_tools.catalog import (
    criar_registro_ferramentas_inna,
    obter_catalogo_schemas_ferramentas,
)
from src.agent_tools.core import (
    ToolCall,
    ToolExecutionContext,
    ToolExecutor,
    ToolStatus,
)
from src.agent_tools.rag_tools import (
    RAG_TOOL_NAME,
    BuscarConhecimentoRagInput,
    RagToolResult,
)


def _context(
    agent: str = "rag_agent",
) -> ToolExecutionContext:
    return ToolExecutionContext(
        requested_by=agent,
        user_id="user-test",
        session_id="thread-test",
        trace_id="trace-test",
    )


def _successful_legacy_result(
) -> RagToolResult:
    return RagToolResult(
        ok=True,
        question=(
            "Como criar uma reserva financeira?"
        ),
        language="pt",
        answer=(
            "Comece definindo uma meta e "
            "guardando uma parte da renda."
        ),
        sources=[
            "guia_reserva_financeira.md",
        ],
        mode=(
            "rag_hibrido_pgvector_text_"
            "neon_rerank"
        ),
        retrieved_documents=3,
        duration_ms=125,
        raw_result={
            "internal": (
                "não deve aparecer na saída formal"
            ),
        },
    )


def test_input_rejects_short_question():
    with pytest.raises(ValidationError):
        BuscarConhecimentoRagInput(
            pergunta="oi",
        )


def test_catalog_registers_formal_rag_tool():
    registry = (
        criar_registro_ferramentas_inna()
    )

    definition = registry.get(
        RAG_TOOL_NAME
    )

    assert definition.name == (
        "buscar_conhecimento_rag"
    )

    assert (
        "rag_agent"
        in definition.allowed_agents
    )

    assert (
        "education_agent"
        in definition.allowed_agents
    )


def test_schema_catalog_exposes_rag_tool():
    catalog = (
        obter_catalogo_schemas_ferramentas()
    )

    rag_definition = next(
        item
        for item in catalog
        if item["name"] == RAG_TOOL_NAME
    )

    properties = rag_definition[
        "input_schema"
    ]["properties"]

    assert "pergunta" in properties
    assert "idioma" in properties
    assert "top_k" in properties


def test_rag_agent_executes_formal_tool():
    registry = (
        criar_registro_ferramentas_inna()
    )

    call = ToolCall(
        tool_name=RAG_TOOL_NAME,
        arguments={
            "pergunta": (
                "Como criar uma reserva financeira?"
            ),
            "idioma": "pt",
            "top_k": 4,
        },
        context=_context(),
    )

    with (
        patch(
            "src.agent_tools.rag_tools."
            "consultar_rag_inna",
            return_value=(
                _successful_legacy_result()
            ),
        ),
        ToolExecutor(
            registry=registry
        ) as executor,
    ):
        result = executor.execute(call)

    assert result.status == ToolStatus.SUCCESS
    assert result.ok is True

    assert result.output["resposta"].startswith(
        "Comece definindo"
    )

    assert result.output[
        "documentos_recuperados"
    ] == 3

    assert "raw_result" not in result.output
    assert "internal" not in str(result.output)


def test_report_agent_cannot_execute_rag_tool():
    registry = (
        criar_registro_ferramentas_inna()
    )

    call = ToolCall(
        tool_name=RAG_TOOL_NAME,
        arguments={
            "pergunta": (
                "Como organizar os gastos?"
            ),
        },
        context=_context(
            agent="report_agent"
        ),
    )

    with ToolExecutor(
        registry=registry
    ) as executor:
        result = executor.execute(call)

    assert result.status == ToolStatus.DENIED

    assert (
        result.error.code
        == "tool_permission_denied"
    )


def test_invalid_arguments_are_rejected_before_rag():
    registry = (
        criar_registro_ferramentas_inna()
    )

    call = ToolCall(
        tool_name=RAG_TOOL_NAME,
        arguments={
            "pergunta": "oi",
            "top_k": 99,
        },
        context=_context(),
    )

    with (
        patch(
            "src.agent_tools.rag_tools."
            "consultar_rag_inna"
        ) as mock_rag,
        ToolExecutor(
            registry=registry
        ) as executor,
    ):
        result = executor.execute(call)

    assert (
        result.status
        == ToolStatus.VALIDATION_ERROR
    )

    mock_rag.assert_not_called()


def test_rag_failure_becomes_safe_tool_error():
    registry = (
        criar_registro_ferramentas_inna()
    )

    failure = RagToolResult(
        ok=False,
        question=(
            "Como organizar minhas finanças?"
        ),
        language="pt",
        error_type="DatabaseInternalError",
        error_message=(
            "informação interna que não deve "
            "ser exposta"
        ),
    )

    call = ToolCall(
        tool_name=RAG_TOOL_NAME,
        arguments={
            "pergunta": (
                "Como organizar minhas finanças?"
            ),
        },
        context=_context(),
    )

    with (
        patch(
            "src.agent_tools.rag_tools."
            "consultar_rag_inna",
            return_value=failure,
        ),
        ToolExecutor(
            registry=registry
        ) as executor,
    ):
        result = executor.execute(call)

    assert result.status == ToolStatus.ERROR

    assert (
        result.error.code
        == "tool_execution_error"
    )

    assert (
        "informação interna"
        not in result.error.message
    )

def test_context_extractor_falls_back_to_documents():
    from src.agent_tools.rag_tools import (
        _extrair_contexto_recuperado,
    )

    result = {
        "contexto_usado": "",
        "documentos": [
            {
                "chunk_text": "Primeiro contexto recuperado.",
            },
            {
                "texto": "Segundo contexto recuperado.",
            },
            {
                "trecho": "Primeiro contexto recuperado.",
            },
        ],
    }

    assert _extrair_contexto_recuperado(result) == [
        "Primeiro contexto recuperado.",
        "Segundo contexto recuperado.",
    ]
