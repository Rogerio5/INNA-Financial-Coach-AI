from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.agent_tools.core import (
    ToolStatus,
)
from src.agent_tools.financial_history_tools import (
    FINANCIAL_HISTORY_TOOL_NAME,
)
from src.agents.financial_history_flow import (
    resolver_limite_historico,
)
from src.agents.nodes import (
    financial_agent_node,
)
from src.agents.schemas import (
    SupervisorLLMDecision,
)
from src.agents.supervisor import (
    classificar_intencao_por_regras,
)
from src.agents.supervisor_llm import (
    _validar_compatibilidade,
)


def _state(
    *,
    message: str = ("Mostre meus últimos 3 diagnósticos."),
    user_id: str | None = "trusted-user-1",
) -> dict:
    return {
        "user_message": message,
        "user_id": user_id,
        "thread_id": "thread-history-1",
        "intent": "historico_financeiro",
        "confidence": 0.96,
        "context": {},
        "tool_results": [],
        "structured_response": {},
        "errors": [],
        "trace": [],
    }


def _success_result(
    *,
    has_history: bool = True,
):
    if has_history:
        output = {
            "possui_historico": True,
            "total_retornado": 1,
            "diagnosticos": [
                {
                    "data_hora": ("2026-07-17T10:30:00"),
                    "saldo_estimado": 1200.5,
                    ("comprometimento_renda_percentual"): 70.25,
                    "meses_reserva_estimados": 2.5,
                    "score_financeiro": 70,
                    "nivel_risco": "Medio",
                    "moeda": "BRL",
                    "idioma": "pt",
                }
            ],
        }
    else:
        output = {
            "possui_historico": False,
            "total_retornado": 0,
            "diagnosticos": [],
        }

    return SimpleNamespace(
        call_id="call-history-1",
        tool_name=(FINANCIAL_HISTORY_TOOL_NAME),
        status=ToolStatus.SUCCESS,
        ok=True,
        duration_ms=4,
        output=output,
        error=None,
    )


@pytest.mark.parametrize(
    "message",
    [
        "Mostre meu histórico financeiro.",
        "Quais foram meus últimos diagnósticos?",
        "Como estava meu score anterior?",
        "Mostre meus últimos 3 diagnósticos.",
    ],
)
def test_supervisor_routes_history_messages(
    message,
):
    decision = classificar_intencao_por_regras(message)

    assert decision.intent == "historico_financeiro"

    assert decision.next_node == "financial_agent"

    assert decision.use_database is True


def test_report_request_has_precedence():
    decision = classificar_intencao_por_regras(
        ("Quero gerar PDF dos meus últimos diagnósticos.")
    )

    assert decision.intent == "relatorio"
    assert decision.next_node == "report_agent"


def test_current_diagnosis_route_is_preserved():
    decision = classificar_intencao_por_regras("Ganho 4000 e gasto 3000.")

    assert decision.intent == "diagnostico_financeiro"

    assert decision.next_node == "financial_agent"


def test_llm_history_route_is_forced():
    decision = SupervisorLLMDecision(
        intent="historico_financeiro",
        next_node="fallback_agent",
        confidence=0.90,
        use_rag=True,
        use_database=False,
        generate_report=True,
        reason="Consulta de histórico.",
    )

    validated = _validar_compatibilidade(decision)

    assert validated.next_node == "financial_agent"

    assert validated.use_database is True
    assert validated.use_rag is False

    assert validated.generate_report is False


def test_history_limit_parser_is_bounded():
    assert resolver_limite_historico("Mostre meus últimos 3 diagnósticos") == 3

    assert resolver_limite_historico("Mostre 8 últimos registros") == 8

    assert resolver_limite_historico("Mostre meus últimos 99 diagnósticos") == 20

    assert resolver_limite_historico("Mostre meu histórico") == 5


def test_history_flow_uses_only_context_identity():
    with (
        patch("src.agents.nodes.resolver_entrada_financeira") as financial_resolver,
        patch(
            "src.agents.financial_history_flow.executar_ferramenta_inna",
            return_value=_success_result(),
        ) as runtime,
    ):
        result = financial_agent_node(_state())

    financial_resolver.assert_not_called()

    runtime.assert_called_once()

    tool_call = runtime.call_args.args[0]

    assert tool_call.tool_name == (FINANCIAL_HISTORY_TOOL_NAME)

    assert tool_call.arguments == {
        "limite": 3,
    }

    assert tool_call.context.user_id == "trusted-user-1"

    assert "usuario_id" not in tool_call.arguments

    assert "user_id" not in tool_call.arguments

    assert result["structured_response"]["historico_financeiro"]["total_retornado"] == 1

    assert result["tool_results"][-1]["tool"] == FINANCIAL_HISTORY_TOOL_NAME

    assert "output" not in result["tool_results"][-1]


def test_history_flow_handles_empty_history():
    with patch(
        "src.agents.financial_history_flow.executar_ferramenta_inna",
        return_value=(_success_result(has_history=False)),
    ):
        result = financial_agent_node(_state(message=("Mostre meu histórico.")))

    assert "não encontrei diagnósticos" in result["response"].lower()

    assert (
        result["structured_response"]["historico_financeiro"]["possui_historico"]
        is False
    )


def test_history_flow_rejects_missing_identity():
    with patch("src.agents.financial_history_flow.executar_ferramenta_inna") as runtime:
        result = financial_agent_node(_state(user_id=None))

    runtime.assert_not_called()

    assert "identidade de usuário validada" in result["response"]

    assert "trusted_user_identity_missing" in result["errors"]
