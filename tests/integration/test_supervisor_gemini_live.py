from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

from src.agents.supervisor_llm import (
    classificar_com_gemini,
)


load_dotenv(
    override=False,
)


def test_supervisor_gemini_live_retorna_schema_valido():
    """
    Teste de integração real.

    Faz uma chamada externa ao Gemini e, portanto,
    não pertence à suíte unitária.
    """
    live_test_enabled = str(
        os.getenv(
            "RUN_LIVE_GEMINI_TESTS",
            "",
        )
    ).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    if not live_test_enabled:
        pytest.skip(
            "Teste real desativado. Defina RUN_LIVE_GEMINI_TESTS=1 para executar."
        )

    configured = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))

    if not configured:
        pytest.skip("Chave do Gemini não configurada.")

    message = (
        "Estou meio perdido e queria entender qual seria o melhor caminho para começar."
    )

    decision = classificar_com_gemini(
        mensagem=message,
        context={
            "current_message": message,
            "rendered_prompt": (
                "Idioma: pt\nMoeda: BRL\nO usuário busca orientação financeira inicial."
            ),
        },
    )

    assert decision.classification_source == "gemini"
    assert decision.gemini_called is True
    assert decision.fallback_used is False

    assert decision.next_node in {
        "financial_agent",
        "education_agent",
        "rag_agent",
        "report_agent",
        "fallback_agent",
    }

    assert 0.0 <= decision.confidence <= 1.0
    assert len(decision.reason.strip()) >= 3
