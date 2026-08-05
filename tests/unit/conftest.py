from __future__ import annotations

import pytest

from src.agents.schemas import (
    SupervisorDecision,
)


@pytest.fixture(autouse=True)
def _bloquear_servicos_externos_em_testes_unitarios(
    monkeypatch,
):
    """
    Impede chamadas externas ao Gemini e ao Phoenix durante
    testes unitários.

    Testes específicos podem sobrescrever esses valores ou mocks.
    """

    monkeypatch.setenv(
        "PHOENIX_ENABLED",
        "false",
    )
    monkeypatch.setenv(
        "PHOENIX_TRACE_SAMPLE_RATE",
        "0.0",
    )
    monkeypatch.setenv(
        "PHOENIX_CAPTURE_CONTENT",
        "false",
    )

    try:
        from src.observability import phoenix_runtime

        monkeypatch.setattr(
            phoenix_runtime,
            "_INITIALIZED",
            False,
        )
        monkeypatch.setattr(
            phoenix_runtime,
            "_TRACER_PROVIDER",
            None,
        )
        monkeypatch.setattr(
            phoenix_runtime,
            "_RUNTIME_SETTINGS",
            None,
        )
        monkeypatch.setattr(
            phoenix_runtime,
            "_RUNTIME_ERROR",
            None,
        )
    except ImportError:
        pass

    def classificador_simulado(
        *,
        mensagem: str,
        context=None,
    ) -> SupervisorDecision:
        return SupervisorDecision(
            intent="desconhecido",
            next_node="fallback_agent",
            confidence=0.20,
            reason=("Classificação LLM simulada durante os testes unitários."),
            classification_source="fallback",
            classification_duration_ms=0,
            gemini_called=False,
            fallback_used=True,
            classification_error=None,
        )

    monkeypatch.setattr(
        ("src.agents.supervisor.classificar_com_gemini"),
        classificador_simulado,
    )
