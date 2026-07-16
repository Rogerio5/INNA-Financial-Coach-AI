from __future__ import annotations

from unittest.mock import patch

from src.agent_tools.rag_tools import (
    RagToolResult,
    _normalizar_fontes,
    consultar_rag_inna,
)
from src.agents.nodes import rag_agent_node


def test_normalizar_fontes_remove_duplicadas():
    fontes = _normalizar_fontes(
        [
            "guia-reserva",
            {"source": "manual-inna"},
            {"titulo": "guia-reserva"},
        ]
    )

    assert fontes == [
        "guia-reserva",
        "manual-inna",
    ]


def test_consultar_rag_rejeita_pergunta_curta():
    resultado = consultar_rag_inna(
        "oi",
        idioma="pt",
    )

    assert resultado.ok is False
    assert (
        resultado.error_type
        == "ValidationError"
    )


@patch(
    "src.agents.nodes."
    "consultar_rag_inna"
)
def test_rag_agent_node_sucesso(
    mock_consultar,
):
    mock_consultar.return_value = (
        RagToolResult(
            ok=True,
            question=(
                "Como criar uma reserva?"
            ),
            language="pt",
            answer=(
                "Comece definindo um valor "
                "mensal possível."
            ),
            sources=[
                "base-reserva-financeira"
            ],
            mode="rag_hibrido",
            retrieved_documents=3,
            duration_ms=125,
        )
    )

    state = {
        "user_message": (
            "Como criar uma reserva?"
        ),
        "language": "pt",
        "intent": "consulta_rag",
        "confidence": 0.80,
        "structured_response": {},
        "tool_results": [],
        "errors": [],
        "trace": [
            "supervisor:consulta_rag"
        ],
    }

    resultado = rag_agent_node(state)

    assert resultado["response"].startswith(
        "Comece definindo"
    )

    assert resultado[
        "structured_response"
    ]["rag_execution"]["ok"] is True

    assert resultado[
        "structured_response"
    ]["agent_response"]["sources"] == [
        "base-reserva-financeira"
    ]

    assert resultado["trace"] == [
        "supervisor:consulta_rag",
        "tool:consultar_rag_inna:start",
        "tool:consultar_rag_inna:success",
        "agent:rag_agent",
    ]


@patch(
    "src.agents.nodes."
    "consultar_rag_inna"
)
def test_rag_agent_node_falha_controlada(
    mock_consultar,
):
    mock_consultar.return_value = (
        RagToolResult(
            ok=False,
            question="Pergunta financeira",
            language="pt",
            duration_ms=20,
            error_type="DatabaseError",
            error_message=(
                "Banco temporariamente "
                "indisponível."
            ),
        )
    )

    state = {
        "user_message": (
            "Pergunta financeira"
        ),
        "language": "pt",
        "intent": "consulta_rag",
        "confidence": 0.80,
        "structured_response": {},
        "tool_results": [],
        "errors": [],
        "trace": [
            "supervisor:consulta_rag"
        ],
    }

    resultado = rag_agent_node(state)

    assert (
        "Não foi possível"
        in resultado["response"]
    )

    assert resultado["errors"] == [
        "Banco temporariamente indisponível."
    ]

    assert (
        resultado["tool_results"][0]["ok"]
        is False
    )
