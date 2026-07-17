from __future__ import annotations

import pytest

from src.agents.schemas import (
    SupervisorDecision,
)


@pytest.fixture(autouse=True)
def _bloquear_gemini_real_em_testes_unitarios(
    monkeypatch,
):
    """
    Impede chamadas externas ao Gemini durante testes
    unitários.

    Testes específicos podem sobrescrever este mock
    usando unittest.mock.patch.
    """

    def classificador_simulado(
        *,
        mensagem: str,
        context=None,
    ) -> SupervisorDecision:
        return SupervisorDecision(
            intent="desconhecido",
            next_node="fallback_agent",
            confidence=0.20,
            reason=(
                "Classificação LLM simulada durante "
                "os testes unitários."
            ),
            classification_source="fallback",
            classification_duration_ms=0,
            gemini_called=False,
            fallback_used=True,
            classification_error=None,
        )

    monkeypatch.setattr(
        (
            "src.agents.supervisor."
            "classificar_com_gemini"
        ),
        classificador_simulado,
    )
